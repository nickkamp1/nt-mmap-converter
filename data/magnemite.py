"""
MagNeMITe custom format data parser.
Handles conversion from parquet files to memory-mapped format.
"""

import pandas as pd
import numpy as np
import os
import glob
from typing import Iterator, Tuple, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.mmap_format import EventRecord, PhotonHit

def group_hits_by_window(hit_times, hit_charges, time_window, return_counts=False):
    """
    Group hits into fixed time windows, returning the first actual hit time
    in each non-empty window and the sum of charges in that window.

    Parameters
    ----------
    hit_times : array-like, shape (N,)
        Hit times in nanoseconds.
    hit_charges : array-like, shape (N,)
        Charge per hit (e.g., photoelectrons). Must align with hit_times.
    time_window : float
        Window size in nanoseconds (> 0).
    return_counts : bool, optional (default: False)
        If True, also return the number of hits per window.

    Returns
    -------
    grouped_times : np.ndarray, shape (M,)
        First actual hit time in each non-empty window (ascending by window).
    window_charges : np.ndarray, shape (M,)
        Sum of hit_charges within each window.
    hit_counts : np.ndarray, shape (M,), optional
        Number of hits in each window (only if return_counts=True).
    """
    ht = np.asarray(hit_times)
    hc = np.asarray(hit_charges)

    if ht.size == 0:
        if return_counts:
            return ht[:0], ht[:0].astype(float), ht[:0]
        else:
            return ht[:0], ht[:0].astype(float)

    if ht.shape != hc.shape:
        raise ValueError("hit_times and hit_charges must have the same shape.")
    if time_window <= 0:
        raise ValueError("time_window must be positive.")

    # Stable sort by time (stable ensures the first time in each bin is preserved if equal times occur).
    order = np.argsort(ht, kind="mergesort")
    st = ht[order]
    sc = hc[order]

    # Compute monotone bin labels with numerically robust arithmetic.
    if np.issubdtype(st.dtype, np.integer) and float(time_window).is_integer():
        tw = np.int64(time_window)
        bins = (st - st[0]) // tw
    else:
        # Cast to float64 and shift by st[0] for better precision at boundaries.
        bins = np.floor((st - st[0]).astype(np.float64) / float(time_window)).astype(np.int64)

    # Run-length encode the (sorted, hence monotone) bin labels.
    changes = np.empty(bins.size, dtype=bool)
    changes[0] = True
    np.not_equal(bins[1:], bins[:-1], out=changes[1:])
    starts = np.flatnonzero(changes)  # start index of each bin-run

    # First hit time per non-empty bin:
    grouped_times = st[starts]

    # Aggregate charges per bin efficiently:
    window_charges = np.add.reduceat(sc, starts)

    if return_counts:
        hit_counts = np.diff(np.r_[starts, st.size])
        return grouped_times, window_charges, hit_counts
    else:
        return grouped_times, window_charges

def find_parquet_files(input_path: str) -> list:
    """
    Find all parquet files in the input directory.

    Args:
        input_path: Directory containing .parquet files

    Returns:
        List of parquet file paths, sorted appropriately
    """
    if not os.path.isdir(input_path):
        raise ValueError(f"Input path is not a directory: {input_path}")

    # Find all parquet files
    pattern = os.path.join(input_path, "*.parquet")
    files = glob.glob(pattern)

    if not files:
        raise ValueError(f"No .parquet files found in {input_path}")

    # Sort alphabetically for consistent ordering
    files.sort()
    return files


def parse_mc_truth(mc_truth_df, filetype=None, dummy_val=-9999.) -> Dict[str, Any]:
    """
    Parse MC truth information from magnemite format.

    Args:
        mc_truth_df: Pandas DataFrame with mc_truth data (single row expected)
        filetype: Type of file being processed (SIREN, NuGen, CORSIKA)

    Returns:
        Cleaned dictionary suitable for EventRecord
    """
    # Extract the first (and should be only) row as a Series
    if len(mc_truth_df) == 0:
        raise ValueError("Empty mc_truth DataFrame")

    # Get the first row as a pandas Series
    row = mc_truth_df.iloc[0]

    if filetype=="SIREN":
        # HNL-specific fields
        parsed = {
            # neutrino
            'initial_energy': float(row['nu_energy']),
            'initial_azimuth': float(row['nu_azimuth']),
            'initial_zenith': float(row['nu_zenith']),
            'initial_x': float(row['nu_pos_x']),
            'initial_y': float(row['nu_pos_y']),
            'initial_z': float(row['nu_pos_z']),
            'initial_type': int(row['nu_pdg']),
            'interaction': 0, # signal events: HNL interactions
            # hadrons
            'final_energy': [float(row['hnl_energy']),
                             float(row['hadrons_energy']),
                             float(row['decay_product_0_energy']), # up to 3 visible decay products
                             float(row['decay_product_1_energy']),
                             float(row['decay_product_2_energy'])
                             ],
            'final_azimuth': [dummy_val, # no HNL dir info for some reason
                              float(row['hadrons_azimuth']),
                              float(row['decay_product_0_azimuth']), # up to 3 visible decay products
                              float(row['decay_product_1_azimuth']),
                              float(row['decay_product_2_azimuth'])
                              ],
            'final_zenith': [dummy_val,
                             float(row['hadrons_zenith']),
                             float(row['decay_product_0_zenith']), # up to 3 visible decay products
                             float(row['decay_product_1_zenith']),
                             float(row['decay_product_2_zenith'])
                             ],
            'final_x': [float(row['hadrons_pos_x']),  # first cascade: hadrons pos
                        float(row['decay_pos_x']) # second cascade: decay pos
                        ],
            'final_y': [float(row['hadrons_pos_y']),  # first cascade: hadrons pos
                        float(row['decay_pos_y']) # second cascade: decay pos
                        ],
            'final_z': [float(row['hadrons_pos_z']),  # first cascade: hadrons pos
                        float(row['decay_pos_z']) # second cascade: decay pos
                        ],
            'final_type': [int(row['hnl_pdg']),
                           2212, # hadrons as proton (2212)
                           int(row['decay_product_0_pdg']),
                           int(row['decay_product_1_pdg']),
                           int(row['decay_product_2_pdg'])
                           ],
            # HNL
            'hnl_length': float(row['hnl_length']),
            'event_weight': float(row['siren_weight']),
        }
    elif filetype=="NuGen":
        # NuGen-specific fields
        parsed = {
            # neutrino
            'initial_energy': float(row['nu_energy']),
            'initial_azimuth': float(row['nu_azimuth']),
            'initial_zenith': float(row['nu_zenith']),
            'initial_x': float(row['nu_pos_x']),
            'initial_y': float(row['nu_pos_y']),
            'initial_z': float(row['nu_pos_z']),
            'initial_type': int(row['nu_pdg']),
            'interaction': 2 if int(row['nu_pdg'])==int(row['lepton_pdg']) else 1, # background events: nu interactions (1 = CC, 2 = NC)
            # hadrons
            'final_energy': [float(row['lepton_energy']),
                             float(row['hadrons_energy']),
                             dummy_val, dummy_val, dummy_val
                             ],
            'final_azimuth': [float(row['lepton_azimuth']),
                              float(row['hadrons_azimuth']),
                              dummy_val, dummy_val, dummy_val
                             ],
            'final_zenith': [float(row['lepton_zenith']),
                             float(row['hadrons_zenith']),
                             dummy_val, dummy_val, dummy_val
                            ],
            'final_x': [float(row['lepton_pos_x']),
                        float(row['hadrons_pos_x'])
                        ],
            'final_y': [float(row['lepton_pos_y']),
                        float(row['hadrons_pos_y'])
                        ],
            'final_z': [float(row['lepton_pos_z']),
                        float(row['hadrons_pos_z'])
                        ],
            'final_type': [int(row['lepton_pdg']),
                           int(row['hadrons_pdg']),
                           int(dummy_val), int(dummy_val), int(dummy_val)
                           ],
            # HNL
            'hnl_length': dummy_val,
            'event_weight': float(row['nugen_weight']),
        }
    elif filetype=="CORSIKA":
        # CORSIKA-specific fields
        parsed = {
            # primary
            'initial_energy': float(row['primary_energy']),
            'initial_azimuth': float(row['primary_azimuth']),
            'initial_zenith': float(row['primary_zenith']),
            'initial_x': float(row['primary_pos_x']),
            'initial_y': float(row['primary_pos_y']),
            'initial_z': float(row['primary_pos_z']),
            'initial_type': int(row['primary_pdg']),
            'interaction': 3, # background events: cosmics
            # no final state
            'final_energy': [dummy_val, dummy_val, dummy_val, dummy_val, dummy_val],
            'final_azimuth': [dummy_val, dummy_val, dummy_val, dummy_val, dummy_val],
            'final_zenith': [dummy_val, dummy_val, dummy_val, dummy_val, dummy_val],
            'final_x': [dummy_val, dummy_val],
            'final_y': [dummy_val, dummy_val],
            'final_z': [dummy_val, dummy_val],
            'final_type': [int(dummy_val), int(dummy_val), int(dummy_val), int(dummy_val), int(dummy_val)],
            # HNL
            'hnl_length': dummy_val,
            'event_weight': float(row['corsika_weight']),
        }
    else:
        raise ValueError(f"Unknown filetype: {filetype}. Supported types: SIREN, NuGen, CORSIKA")

    # Common fields for all file types
    parsed['run_id'] = int(row['run_id'])
    parsed['event_id'] = int(row['event_id'])
    parsed['homogenized_qtot'] = float(row['Homogenized_QTot'])
    parsed['BDT_pred'] = float(row.get('BDT_pred', -1.0))
    # Classification fields
    parsed['classification'] = int(row.get('classification', -9999))
    parsed['morphology'] = int(row.get('morphology', -9999))
    parsed['is_signal'] = bool(row.get('is_signal', False))
    parsed['is_background'] = bool(row.get('is_background', False))

    # Initialize selected filter-pass booleans (used as input to BDT in Mag0)
    selected_filters = {
        "GRECOOnlineFilter_19": "filter_grecoonline_19",
        "DeepCoreFilter_13": "filter_deepcore_13",
        "LowUp_13": "filter_lowup_13",
        "FSSCandidate_13": "filter_fsscandidate_13",
        "OnlineL2Filter_17": "filter_onlinel2_17",
        "MuonFilter_13": "filter_muon_13",
        "FSSFilter_13": "filter_fss_13",
        "CascadeFilter_13": "filter_cascade_13",
        "MESEFilter_15": "filter_mese_15"
    }
    for filter_key, out_name in selected_filters.items():
        if filter_key in row:
            parsed[out_name] = bool(row[filter_key])
        else:
            parsed[out_name] = False

    return parsed


def parse_photons(photons_df) -> Dict[str, np.ndarray]:
    """
    Parse photon information from Magnemite format.

    Handles the case where photons_df has nested arrays (one row per event,
    each column contains array of pulse values) or flat structure (one row per pulse).

    Args:
        photons_df: Pandas DataFrame with photon data

    Returns:
        Cleaned dictionary suitable for PhotonHit
    """
    # Check if we have nested arrays (MagNeMITe parquet format)
    # In this format, each row is an event and columns like x contain arrays of pulse values
    if len(photons_df) > 0 and hasattr(photons_df["x"].iloc[0], "__len__") and not isinstance(photons_df["x"].iloc[0], str):
        # Nested array format - concatenate all arrays
        x_vals = np.concatenate(photons_df["x"].values)
        y_vals = np.concatenate(photons_df["y"].values)
        z_vals = np.concatenate(photons_df["z"].values)
        time_vals = np.concatenate(photons_df["time"].values)
        charge_vals = np.concatenate(photons_df["charge"].values)
        string_vals = np.concatenate(photons_df["string"].values)
        om_vals = np.concatenate(photons_df["om"].values)

        # For run_id, need to repeat for each pulse in each event
        run_ids = []
        for idx, row in photons_df.iterrows():
            n_pulses = len(row["x"])
            run_ids.extend([row["run_id"]] * n_pulses)
        run_id_vals = np.array(run_ids)

        return {
            "sensor_pos_x": x_vals.astype(np.float32),
            "sensor_pos_y": y_vals.astype(np.float32),
            "sensor_pos_z": z_vals.astype(np.float32),
            "t": time_vals.astype(np.float32),
            "charge": charge_vals.astype(np.float32),
            "string_id": string_vals.astype(np.uint32),
            "sensor_id": om_vals.astype(np.uint32),
            "run_id": run_id_vals.astype(np.uint64),
            "id_idx": np.zeros(len(x_vals), dtype=np.uint64),
        }
    else:
        # Flat format - direct access
        return {
            "sensor_pos_x": photons_df["x"].values.astype(np.float32),
            "sensor_pos_y": photons_df["y"].values.astype(np.float32),
            "sensor_pos_z": photons_df["z"].values.astype(np.float32),
            "t": photons_df["time"].values.astype(np.float32),
            "charge": photons_df["charge"].values.astype(np.float32),
            "string_id": photons_df["string"].values.astype(np.uint32),
            "sensor_id": photons_df["om"].values.astype(np.uint32),
            "run_id": photons_df["run_id"].values.astype(np.uint64),
            "id_idx": np.zeros_like(photons_df["event_id"].values, dtype=np.uint64),
        }


def process_photons_with_grouping(photons_dict: Dict[str, np.ndarray],
                                 grouping_window_ns: float) -> Dict[str, np.ndarray]:
    """
    Process photons with optional hit grouping per sensor.

    Args:
        photons_dict: Raw photons dictionary from parquet
        grouping_window_ns: Time window for grouping hits by sensor (0 = no grouping)

    Returns:
        Processed photons dictionary with optional grouping applied
    """
    if grouping_window_ns <= 0:
        # No grouping - return raw hits with charge=1
        result = parse_photons(photons_dict)
        return result

    # Optimized unique sensor detection using safe hash-based approach
    string_ids = photons_dict['string']
    sensor_ids = photons_dict['om']

    # Create safe combined keys using hash of (string_id, sensor_id) pairs
    # This avoids overflow issues and works with any sensor ID size
    sensor_pairs = np.column_stack((string_ids, sensor_ids))

    # Use lexsort to get sorted indices, then find unique groups
    sort_indices = np.lexsort((sensor_ids, string_ids))
    sorted_pairs = sensor_pairs[sort_indices]

    # Find boundaries where (string_id, sensor_id) changes
    unique_mask = np.ones(len(sorted_pairs), dtype=bool)
    unique_mask[1:] = (sorted_pairs[1:] != sorted_pairs[:-1]).any(axis=1)
    unique_indices = np.where(unique_mask)[0]

    # Pre-allocate result arrays with better size estimation
    n_photons = len(photons_dict['time'])
    n_unique_sensors = len(unique_indices)
    estimated_grouped = max(n_photons // 5, n_unique_sensors)  # Better estimate

    all_times = np.empty(estimated_grouped, dtype=np.float32)
    all_charges = np.empty(estimated_grouped, dtype=np.float32)
    all_sensor_pos_x = np.empty(estimated_grouped, dtype=np.float32)
    all_sensor_pos_y = np.empty(estimated_grouped, dtype=np.float32)
    all_sensor_pos_z = np.empty(estimated_grouped, dtype=np.float32)
    all_string_ids = np.empty(estimated_grouped, dtype=np.uint32)
    all_sensor_ids = np.empty(estimated_grouped, dtype=np.uint32)
    all_id_idx = np.empty(estimated_grouped, dtype=np.uint64)

    result_idx = 0

    # Process each unique sensor
    for i, unique_idx in enumerate(unique_indices):
        string_id, sensor_id = sorted_pairs[unique_idx]

        # Find end of this sensor group
        if i < len(unique_indices) - 1:
            end_idx = unique_indices[i + 1]
        else:
            end_idx = len(sorted_pairs)

        # Get original indices for this sensor group
        sensor_original_indices = sort_indices[unique_idx:end_idx]
        sensor_times = photons_dict['time'][sensor_original_indices]
        sensor_charges = photons_dict['charge'][sensor_original_indices]

        if len(sensor_times) == 0:
            continue

        # Group hits by time window for this sensor
        grouped_times, grouped_charges = group_hits_by_window(
            sensor_times, sensor_charges, grouping_window_ns
        )

        if len(grouped_times) == 0:
            continue

        # Get metadata from first photon of this sensor
        first_original_idx = sensor_original_indices[0]
        n_grouped = len(grouped_times)

        # Ensure we have enough space
        while result_idx + n_grouped > len(all_times):
            # Double the array size
            new_size = len(all_times) * 2
            all_times = np.resize(all_times, new_size)
            all_charges = np.resize(all_charges, new_size)
            all_sensor_pos_x = np.resize(all_sensor_pos_x, new_size)
            all_sensor_pos_y = np.resize(all_sensor_pos_y, new_size)
            all_sensor_pos_z = np.resize(all_sensor_pos_z, new_size)
            all_string_ids = np.resize(all_string_ids, new_size)
            all_sensor_ids = np.resize(all_sensor_ids, new_size)
            all_id_idx = np.resize(all_id_idx, new_size)

        # Copy data efficiently using array slicing
        end_result_idx = result_idx + n_grouped
        all_times[result_idx:end_result_idx] = grouped_times
        all_charges[result_idx:end_result_idx] = grouped_charges
        all_sensor_pos_x[result_idx:end_result_idx] = photons_dict['x'][first_original_idx]
        all_sensor_pos_y[result_idx:end_result_idx] = photons_dict['y'][first_original_idx]
        all_sensor_pos_z[result_idx:end_result_idx] = photons_dict['z'][first_original_idx]
        all_string_ids[result_idx:end_result_idx] = string_id
        all_sensor_ids[result_idx:end_result_idx] = sensor_id
        all_id_idx[result_idx:end_result_idx] = np.zeros(len(grouped_times), dtype=np.uint64)

        result_idx = end_result_idx

    # Trim arrays to actual size and return
    return {
        'sensor_pos_x': all_sensor_pos_x[:result_idx].copy(),
        'sensor_pos_y': all_sensor_pos_y[:result_idx].copy(),
        'sensor_pos_z': all_sensor_pos_z[:result_idx].copy(),
        't': all_times[:result_idx].copy(),
        'charge': all_charges[:result_idx].copy(),
        'string_id': all_string_ids[:result_idx].copy(),
        'sensor_id': all_sensor_ids[:result_idx].copy(),
        'id_idx': all_id_idx[:result_idx].copy(),
    }




def iter_magnemite_events(parquet_files: list, filetype: str, cuts: str = None) -> Iterator[Tuple[Dict[str, Any], Dict[str, np.ndarray]]]:
    """
    Iterate over all events in MagNeMITe parquet files.

    Args:
        parquet_files: List of parquet event file paths
        filetype: name of generator
        cuts: any cuts to apply to the data

    Yields:
        Tuple of (mc_truth_dict, photons_dict) for each event
    """
    for event_file_path in parquet_files:
        print(f"Processing {os.path.basename(event_file_path)}...")
        pulse_file_path = event_file_path.replace("event", "SRTInIcePulses")
        if not os.path.isfile(pulse_file_path):
            print(f"Warning: Corresponding pulse file not found for {event_file_path}. Skipping.")
            continue
        try:
            event_df = pd.read_parquet(event_file_path)
            if cuts is not None:
                event_df.query(cuts,inplace=True)
            pulse_df = pd.read_parquet(pulse_file_path)
        except Exception as e:
            print(f"Error reading {event_file_path}: {e}")
            continue

        for event_id in event_df["event_id"].unique():
            # Extract mc_truth
            mc_truth_raw = event_df[event_df["event_id"] == event_id]
            mc_truth = parse_mc_truth(mc_truth_raw,filetype=filetype)

            # Extract photons
            photons_raw = pulse_df[pulse_df["event_id"] == event_id]

            yield mc_truth, photons_raw


def convert_magnemite_to_mmap(input_path: str, output_path: str,
                              file_range: str = None, grouping_window_ns: float = 0.0,
                              filetype: str = None, cuts: str = None) -> Tuple[int, int]:
    """
    Convert MagNeMITe parquet files to memory-mapped format using streaming approach.

    Args:
        input_path: Directory containing chunk_*.parquet files
        output_path: Output path for memory-mapped files (without extension)
        file_range: Range of files to convert, e.g., '0-100' or '100-115'
        grouping_window_ns: Time window for hit grouping per sensor (0 = no grouping)
        filteype: type of generator
        cuts: any cuts to apply to the data

    Returns:
        Tuple of (num_events_converted, total_photons)
    """

    # Find input files
    parquet_files = find_parquet_files(input_path)
    print(f"Found {len(parquet_files)} parquet files")

    # Limit files if specified
    if file_range:
        try:
            start, end = map(int, file_range.split('-'))
            parquet_files = parquet_files[start:end]
            print(f"Processing files from index {start} to {end}")
        except ValueError:
            print(f"Invalid file range format: {file_range}. Processing all files.")

    print(f"Converting events from {len(parquet_files)} files using streaming approach...")

    # Create streaming memory-mapped files
    from core.mmap_format import create_streaming_mmap_files, StreamingIndexWriter, append_photons_to_file

    # Estimate events per file for initial allocation (follow icecube expectation)
    events_per_file_estimate = 1000
    initial_estimate = len(parquet_files) * events_per_file_estimate

    idx_path, data_file_path = create_streaming_mmap_files(output_path, initial_estimate, source_type='magnemite')
    index_writer = StreamingIndexWriter(idx_path, initial_estimate)

    # Convert events
    total_photons = 0
    current_photon_idx = 0

    for mc_truth, photons_raw in iter_magnemite_events(parquet_files,filetype=filetype,cuts=cuts):
        # Process photons with optional grouping
        photons = process_photons_with_grouping(photons_raw, grouping_window_ns)

        # Create photon array
        photon_array = PhotonHit.from_dict(photons)
        num_photons = len(photon_array)

        # Skip events with no photons - they're not useful for ML training
        if num_photons == 0:
            continue

        # Compute hit statistics
        mc_truth['num_hits'] = num_photons
        # Count unique sensor/string ID pairs (channels) for Prometheus
        sensor_string_pairs = np.column_stack([photons['string_id'], photons['sensor_id']])
        unique_channels = np.unique(sensor_string_pairs, axis=0)
        mc_truth['num_chans'] = len(unique_channels)

        # Create event record using Magnemite-specific dtype
        event_record = EventRecord.from_dict(mc_truth, source_type='magnemite')

        # Set photon indexing information
        event_record['photon_start_idx'] = current_photon_idx
        event_record['photon_end_idx'] = current_photon_idx + num_photons

        # Write event record (with dynamic growth)
        index_writer.write_event(event_record)

        # Append photons to data file
        append_photons_to_file(data_file_path, photon_array)
        current_photon_idx += num_photons
        total_photons += num_photons

        # Progress reporting
        if index_writer.event_count % 1000 == 0:
            print(f"Processed {index_writer.event_count:,} events, {total_photons:,} photons")

    # Finalize index file
    final_event_count = index_writer.finalize()

    print(f"Conversion complete: {final_event_count:,} events, {total_photons:,} total photons")
    print(f"Output files: {output_path}.idx, {output_path}.dat")

    return final_event_count, total_photons