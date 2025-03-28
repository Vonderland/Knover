#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Plato Reader."""

import numpy as np

from knover.data.dialog_reader import DialogReader
from knover.utils import mask, pad_batch_data


class PlatoReader(DialogReader):
    """The implement of PlatoReader"""

    def __init__(self, args):
        super(PlatoReader, self).__init__(args)
        self.use_bow = args.use_bow

    def _pad_batch_records(self, batch_records, is_infer, **kwargs):
        """Padding a batch of records and construct model's inputs."""
        batch = {}
        batch_token_ids = [record.token_ids for record in batch_records]
        batch_type_ids = [record.type_ids for record in batch_records]
        batch_pos_ids = [record.pos_ids for record in batch_records]
        if self.use_role:
            batch_role_ids = [record.role_ids for record in batch_records]
        batch_tgt_start_idx = [record.tgt_start_idx for record in batch_records]

        batch_size = len(batch_token_ids)

        # padding
        batch["token_ids"] = pad_batch_data(batch_token_ids, pad_id=self.pad_id)
        batch["type_ids"] = pad_batch_data(batch_type_ids, pad_id=0)
        batch["pos_ids"] = pad_batch_data(batch_pos_ids, pad_id=0)
        if self.use_role:
            batch["role_ids"] = pad_batch_data(batch_role_ids, pad_id=0)

        batch["generation_mask"] = self._gen_self_attn_mask(
            batch_token_ids,
            batch_tgt_start_idx=batch_tgt_start_idx,
            is_unidirectional=True,
            num_aux_token=1)
        if not is_infer:
            batch["recognition_mask"] = self._gen_self_attn_mask(
                batch_token_ids,
                is_unidirectional=False,
                num_aux_token=1)

        if is_infer:
            tgt_ids = np.array([[[self.bos_id]]] * batch_size, dtype="int64")
            if self.position_style == "continuous":
                tgt_pos = np.array(batch_tgt_start_idx, dtype="int64")
            else:
                tgt_pos = np.zeros_like(batch_tgt_start_idx, dtype="int64")
            tgt_pos = tgt_pos.reshape(-1, 1, 1)
            batch["init_score"] = np.zeros_like(tgt_ids, dtype="float32").reshape(-1, 1).tolist()
            batch["tgt_ids"] = tgt_ids.tolist()
            batch["tgt_pos"] = tgt_pos.tolist()
            batch["parent_idx"] = np.array(range(batch_size), dtype="int32")
            batch["latent_id"] = np.zeros([batch_size], dtype="int32")

            batch["tgt_generation_mask"] = batch["generation_mask"][:, 0:1, :].astype("float32")

            batch_data_id = [record.data_id for record in batch_records]
            batch["data_id"] = np.array(batch_data_id).astype("int64").reshape([-1, 1])
        else:
            mask_return_list = mask(
                batch_tokens=batch_token_ids,
                vocab_size=self.vocab_size,
                tgt_starts=batch_tgt_start_idx,
                is_unidirectional=True,
                use_latent=True,
                use_bow=self.use_bow)
            batch["tgt_label"] = mask_return_list[0]
            batch["tgt_idx"] = mask_return_list[1]
            if self.use_bow:
                batch["bow_label"] = mask_return_list[2]
                batch["bow_idx"] = mask_return_list[3]

        return batch
