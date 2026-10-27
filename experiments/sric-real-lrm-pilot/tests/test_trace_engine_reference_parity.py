from types import SimpleNamespace
import torch

from sric_real_lrm.adapters.multimode_coconut import CoconutTraceEngine


class ToyBase(torch.nn.Module):
    def __init__(self, vocab: int = 19, hidden: int = 7):
        super().__init__()
        torch.manual_seed(13)
        self.projection = torch.nn.Linear(hidden, vocab, bias=False)
        torch.nn.init.normal_(self.projection.weight, std=0.15)

    def forward(self, *, inputs_embeds, attention_mask=None, position_ids=None, past_key_values=None,
                output_hidden_states=False, use_cache=True):
        hidden = torch.tanh(inputs_embeds * 0.73 - 0.07)
        logits = self.projection(hidden)
        past_len = 0 if past_key_values is None else past_key_values[0][0].shape[2]
        total = past_len + inputs_embeds.shape[1]
        key = torch.zeros(inputs_embeds.shape[0], 1, total, 1)
        value = torch.zeros_like(key)
        return SimpleNamespace(logits=logits, hidden_states=(hidden,), past_key_values=((key, value),))


class ToyCoconut:
    def __init__(self):
        torch.manual_seed(5)
        self.base_causallm = ToyBase()
        self._embedding = torch.nn.Embedding(19, 7)
        self.latent_token_id = 18

    def get_embedding(self):
        return self._embedding


def reference_source_forward(coconut, input_ids, attention_mask, position_ids):
    latent_indices = (input_ids == coconut.latent_token_id).nonzero()
    latent_lists = [[idx[1].item() for idx in latent_indices if idx[0] == batch]
                    for batch in range(input_ids.shape[0])]
    max_n_latents = max(len(items) for items in latent_lists)
    next_compute_range = (0, input_ids.shape[1])
    inputs_embeds = coconut.get_embedding()(input_ids).clone()
    if max_n_latents > 0:
        next_compute_range = (0, latent_indices[:, 1].min().item())
    kv_cache = None
    logits = []
    for pass_idx in range(max_n_latents):
        start, end = next_compute_range
        if kv_cache is None:
            outputs = coconut.base_causallm(
                inputs_embeds=inputs_embeds[:, start:end, :],
                attention_mask=attention_mask[:, start:end],
                position_ids=position_ids[:, start:end],
                output_hidden_states=True,
            )
            offset = 0
        else:
            past = [(k[:, :, :start, :], v[:, :, :start, :]) for k, v in kv_cache]
            outputs = coconut.base_causallm(
                inputs_embeds=inputs_embeds[:, start:end, :],
                attention_mask=attention_mask[:, :end],
                position_ids=position_ids[:, start:end],
                past_key_values=past,
                output_hidden_states=True,
            )
            offset = start
        logits.append(outputs.logits)
        next_compute_range = (end, input_ids.shape[1] if pass_idx + 1 >= max_n_latents else end + 1)
        hidden = outputs.hidden_states[-1]
        kv_cache = outputs.past_key_values
        tensor_list = [[inputs_embeds[b, pos, :] for pos in range(inputs_embeds.shape[1])]
                       for b in range(inputs_embeds.shape[0])]
        for batch, positions in enumerate(latent_lists):
            if len(positions) > pass_idx:
                token_idx = positions[pass_idx]
                tensor_list[batch][token_idx] = hidden[batch, token_idx - 1 - offset, :]
        inputs_embeds = torch.stack([torch.stack(row) for row in tensor_list])
    start, end = next_compute_range
    past = [(k[:, :, :start, :], v[:, :, :start, :]) for k, v in kv_cache] if kv_cache else None
    outputs = coconut.base_causallm(
        inputs_embeds=inputs_embeds[:, start:end, :],
        attention_mask=attention_mask[:, :end],
        position_ids=position_ids[:, start:end],
        past_key_values=past,
        output_hidden_states=True,
    )
    logits.append(outputs.logits)
    return torch.cat(logits, dim=-2), inputs_embeds


def test_trace_engine_matches_reviewed_source_recurrence():
    coconut = ToyCoconut()
    engine = CoconutTraceEngine(coconut)
    input_ids = torch.tensor([[2, 3, 18, 18, 18, 4, 5, 6]])
    attention = torch.ones_like(input_ids)
    positions = torch.arange(input_ids.shape[1]).reshape(1, -1)
    labels = input_ids.clone()
    labels[:, :6] = -100
    reference_logits, reference_embeds = reference_source_forward(coconut, input_ids, attention, positions)
    _, engine_logits, engine_trace = engine.run(
        input_ids=input_ids,
        attention_mask=attention,
        position_ids=positions,
        labels=labels,
    )
    latent_positions = (input_ids[0] == coconut.latent_token_id).nonzero(as_tuple=True)[0]
    assert torch.allclose(reference_logits, engine_logits, atol=0, rtol=0)
    assert torch.allclose(reference_embeds[0, latent_positions], engine_trace, atol=0, rtol=0)
