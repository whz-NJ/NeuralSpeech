# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME

export MKL_THREADING_LAYER=GNU

DATA_PATH=/root/extracted/AA.bin
export PYTHONPATH=$EXP_HOME/FC_utils:$PYTHONPATH
echo "6.1 train"

SAVE_DIR=/root/fastcorrect/models/pretrain.wiki
export CUDA_VISIBLE_DEVICES=0
fairseq-train $DATA_PATH --task fastcorrect \
        --arch fastcorrect --lr 5e-4 --lr-scheduler inverse_sqrt \
        --length-loss-factor 0.5 \
        --noise full_mask \
        --src-with-werdur \
        --skip-invalid-size-inputs-valid-test \
        --dur-predictor-type "v2" \
        --dropout 0.3 --weight-decay 0.0001 \
        --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
        --criterion fc_loss --label-smoothing 0.1 \
        --max-tokens 9000 \
        --werdur-max-predict 3 \
        --assist-edit-loss \
        --save-dir $SAVE_DIR \
        --user-dir $EXP_HOME/FastCorrect \
        --left-pad-target False \
        --left-pad-source False \
        --encoder-layers 6 --decoder-layers 6 \
        --max-epoch 30 --update-freq 4 --fp16 --num-workers 16 \
        --share-all-embeddings --encoder-embed-dim=512 --decoder-embed-dim=512

