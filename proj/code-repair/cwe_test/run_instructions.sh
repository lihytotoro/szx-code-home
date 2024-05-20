CUDA_VISIBLE_DEVICES="0,1,2,4,5,6" torchrun --nproc_per_node 1 testing_cwe_codellama.py \
    --ckpt_dir /data/lihy/codellama/codellama/CodeLlama-7b-Instruct/ \
    --tokenizer_path /data/lihy/codellama/codellama/CodeLlama-7b-Instruct/tokenizer.model \
    --max_seq_len 8192 --max_batch_size 1 --buggy_path ./testcase.c