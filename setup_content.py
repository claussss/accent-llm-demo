
import os
import shutil
import json

# Configuration
MANIFEST_PATH = "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/scripts/benchmarks/manifests/test_manifest_usa_for_TEST.txt"
DEST_BASE = "/home/yurii/Projects/LLM_AC/accent-llm-demo"
AUDIO_MAP = {
    "us_real": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/usa_gt_TEST",
    "indian_real": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_gt_TEST",
    "us_tts": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/usa_TEST",
    "indian_tts_no_exag": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_TEST_no_exaggeration",
    "indian_tts_exag": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_TEST",
    "llm_no_exag": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_TEST_LLM_Cartoon",
    "llm_exag": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_TEST_LLM_Cartoon_exag",
    "llm_exag_adapt": "/home/yurii/Projects/LLM_AC/ubisoft-laforge-daft-exprt/outputs/indian_TEST_LLM_Cartoon_exag_spk_adpt"
}

def setup_content():
    # 1. Parse Manifest for Transcripts
    transcripts = []
    with open(MANIFEST_PATH, 'r') as f:
        for line in f:
            if not line.strip(): continue
            # Format: path|transcript
            parts = line.strip().split('|')
            if len(parts) >= 2:
                transcripts.append(parts[1])
    
    print(f"Found {len(transcripts)} transcripts.")

    # 2. Copy Audios and build data structure
    # We rely on the order of files in the directory matching the manifest order,
    # or simple numeric sorting if filenames are indexed.
    # Looking at ls output from previous turn: "0_symbol_prosody_line0_..."
    # The filenames seem to have an index: line0, line1, etc.
    
    # We will look for files containing "line{i}"
    
    data = {"systems": []}

    for sys_key, source_dir in AUDIO_MAP.items():
        print(f"Processing {sys_key} from {source_dir}...")
        
        # Get all wav files
        all_files = [f for f in os.listdir(source_dir) if f.endswith('.wav')]
        
        # Sort them? Ideally we match line{i}
        # Let's try to find file for each index 0..3
        
        copied_files = []
        for i in range(len(transcripts)):
            # Find file matching pattern for index i
            # Pattern assumption: contains "line{i}_" or starts with "{i}_"
            # Previous ls showed: 0_symbol_prosody_line0_...
            
            match = None
            for fname in all_files:
                # Robust check for index. 
                # Check for "line{i}_" or "_{i}_" or just starting with "{i}_"
                # Based on ls output: "0_symbol_prosody_line0_spk_10_ref_36_audio_ref.wav"
                if f"line{i}_" in fname:
                    match = fname
                    break
                # Fallback if specific naming differs but order is relied upon?
                # The user said: "audios are in the same order in their dirs as this transcipt file row order"
                # So if we can't match by name, sorting might be safer if names are consistent.
            
            if not match:
                # If no explicit line marker found, fall back to sorting and taking ith index
                sorted_files = sorted(all_files)
                if i < len(sorted_files):
                    match = sorted_files[i]
            
            if match:
                src_file = os.path.join(source_dir, match)
                dest_filename = f"utt_{i}.wav"
                dest_path = os.path.join(DEST_BASE, "assets", "audios", sys_key, dest_filename)
                
                shutil.copy2(src_file, dest_path)
                copied_files.append(f"assets/audios/{sys_key}/{dest_filename}")
            else:
                print(f"WARNING: Could not find audio for index {i} in {sys_key}")
                copied_files.append(None)

        data["systems"].append({
            "id": sys_key,
            "audios": copied_files
        })
    
    data["transcripts"] = transcripts
    
    # Save metadata for HTML generation
    with open(os.path.join(DEST_BASE, "content.json"), 'w') as f:
        json.dump(data, f, indent=2)

    print("Content setup complete.")

if __name__ == "__main__":
    setup_content()
