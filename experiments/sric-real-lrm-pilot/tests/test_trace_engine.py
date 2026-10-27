from types import SimpleNamespace
import torch

from sric_real_lrm.adapters.multimode_coconut import CoconutTraceEngine


class ToyBase(torch.nn.Module):
    def __init__(self, vocab: int = 17, hidden: int = 8):
        super().__init__()
        self.projection = torch.nn.Linear(hidden, vocab, bias=False)
        torch.manual_seed(9)
        torch.nn.init.normal_(self.projection.weight, std=0.2)

    def forward(
        self,
        *,
        inputs_embeds,
        attention_mask=None,
        position_ids=None,
        past_key_values=None,
        output_hidden_states=False,
        use_cache=True,
    ):
        hidden = torch.tanh(inputs_embeds * 0.8 + 0.13)
        logits = self.projection(hidden)
        past_len = 0 if past_key_values is None else past_key_values[0][0].shape[2]
        total = past_len + inputs_embeds.shape[1]
        key = torch.zeros(inputs_embeds.shape[0], 1, total, 1, dtype=inputs_embeds.dtype)
        value = torch.zeros_like(key)
        return SimpleNamespace(
            logits=logits,
            hidden_states=(hidden,),
            past_key_values=((key, value),),
        )


class ToyCoconut:
    def __init__(self):
        torch.manual_seed(4)
        self.base_causallm = ToyBase()
        self._embedding = torch.nn.Embedding(17, 8)
        self.latent_token_id = 16

    def get_embedding(self):
        return self._embedding


def test_trace_engine_exact_replay_and_intervention():
    coconut = ToyCoconut()
    engine = CoconutTraceEngine(coconut)
    input_ids = torch.tensor([[1, 2, 16, 16, 3, 4, 5]])
    attention = torch.ones_like(input_ids)
    positions = torch.arange(input_ids.shape[1]).reshape(1, -1)
    labels = input_ids.clone()
    labels[:, :5] = -100
    clean_loss, clean_logits, trace = engine.run(
        input_ids=input_ids,
        attention_mask=attention,
        position_ids=positions,
        labels=labels,
    )
    replay_loss, replay_logits, replay_trace = engine.run(
        input_ids=input_ids,
        attention_mask=attention,
        position_ids=positions,
        labels=labels,
        override_trace=trace,
    )
    assert torch.equal(trace, replay_trace)
    assert torch.allclose(clean_logits, replay_logits, atol=0, rtol=0)
    assert torch.allclose(clean_loss, replay_loss, atol=0, rtol=0)

    altered = trace.flip(0)
    _, altered_logits, _ = engine.run(
        input_ids=input_ids,
        attention_mask=attention,
        position_ids=positions,
        labels=labels,
        override_trace=altered,
    )
    assert not torch.allclose(clean_logits, altered_logits)
