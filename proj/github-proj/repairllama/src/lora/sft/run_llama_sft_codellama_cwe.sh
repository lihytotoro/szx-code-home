export CUDA_VISIBLE_DEVICES="0,1,2,3"
accelerate launch --main_process_port 29501 llama_sft.py \
    --model_name_or_path /data/lihy/codellama/CodeLlama-7b-Instruct-hf \
    --data_path /data/lihy/datasets/java-juliet/src/parsed_dataset/parquet \
    --train_file finetuning_data_maxlen=1024_usertype=repairllama_dataset=codellama-cwe_trainratio=0.9_split=train.parquet \
    --eval_file finetuning_data_maxlen=1024_usertype=repairllama_dataset=codellama-cwe_trainratio=0.9_split=train.parquet \
    --is_lora True \
    --resume_from_checkpoint False \
    --resume_model_path None \
    --model_max_length 1024 \
    --cache_path /data/lihy/training_output/codellama-cwe/cache \
    --do_train \
    --do_eval False \
    --fp16 True \
    --output_dir /data/lihy/training_output/codellama-cwe/finetuned-models_maxlen=1024_epoch=2_input-format=new \
    --num_train_epochs 2 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --eval_steps 10 \
    --save_steps 150 \
    --learning_rate 5e-4 \
    --lr_scheduler_type "cosine" \
    --logging_steps 10 \
    --ddp_find_unused_parameters False \
