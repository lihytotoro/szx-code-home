python backfill_and_test_for_func.py \
    --input_infos_path /data/public/multimodal/lihaoyu/szx/datasets/d4j-processed/processed/defects4j_all_single_func_repairllama_wo_initial_prompt.jsonl \
    --output_patches_path /data/public/multimodal/lihaoyu/szx/testing_output/d4j-output/single_func/defects4j_all_single_func_repairllama_test_output_maxlen=1024_epoch=3_newdata_wo_comment.jsonl \
    --write_outcome_csv_dir /home/lihaoyu/szx/proj/code-repair/mycode/output/single_func/output_csv/purely_for_test \
    --start_patch_idx 9 \
    --end_patch_idx 9 \
    --backfill_base_dir /data/lihy/defects4j-10 \
    --target_file_path_path ../output/single_func/backfill_paths/backfill_path_10.json \
    --timeout_file ../time_compile_test/single_func_buggy_ver.csv