#!/bin/bash
set -ex

function download_tar() {
    remote_path=$1
    local_path=$2
    if [[ ! -e $local_path ]]; then
        echo "Downloading ${local_path} ..."
        wget $remote_path

        the_tar=$(basename ${remote_path})
        the_dir=$(tar tf ${the_tar} | head -n 1)
        tar xf ${the_tar}
        rm ${the_tar}

        local_dirname=$(dirname ${local_path})
        mkdir -p ${local_dirname}

        if [[ $(readlink -f ${the_dir}) != $(readlink -f ${local_path}) ]]; then
            mv ${the_dir} ${local_path}
        fi

        echo "${local_path} has been processed."
    else
        echo "${local_path} is exist."
    fi
}

# download models
mkdir -p models
# pre-trained models
# 24L NSP
download_tar https://dialogue.bj.bcebos.com/Knover/projects/PLATO-KAG/24L_NSP.tar models/24L_NSP
# 24L SU
download_tar https://dialogue.bj.bcebos.com/Knover/projects/PLATO-KAG/24L_SU.tar models/24L_SU

# fine-tuned model
download_tar https://dialogue.bj.bcebos.com/Knover/projects/PLATO-KAG/holle/24L_PLATO_KAG.tar models/24L_PLATO_KAG

# download dataset
# our provided dataset has been preprocessed to get similar data format with wow
# we use the preprocessing script from skt (https://github.com/bckim92/sequential-knowledge-transformer/blob/master/data/holle.py)
download_tar https://dialogue.bj.bcebos.com/Knover/projects/PLATO-KAG/holle/data.tar data

# change to the root directory of Knover
cd ../../..
MODEL_PATH="$PWD/projects/PLATO-KAG/holle/models"

bash ./projects/PLATO-KAG/holle/init_dual_params.sh $MODEL_PATH/24L_NSP $MODEL_PATH/24L_SU $MODEL_PATH/24L_KAG_INIT





