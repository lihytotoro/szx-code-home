CUDA_VISIBLE_DEVICES="0,1,2,3,4,5,6,7" torchrun --nproc_per_node 1 example_instructions.py \
    --ckpt_dir /data/lihy/codellama/codellama/CodeLlama-7b-Instruct/ \
    --tokenizer_path /data/lihy/codellama/codellama/CodeLlama-7b-Instruct/tokenizer.model \
    --max_seq_len 4096 --max_batch_size 1 --original_idx 0 --stop_idx 470