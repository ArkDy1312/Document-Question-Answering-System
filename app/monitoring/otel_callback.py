from langchain.callbacks.base import BaseCallbackHandler
from opentelemetry import trace

class OpenTelemetryCallback(BaseCallbackHandler):
    def __init__(self, name="langchain-span"):
        self.tracer = trace.get_tracer(name)

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.span = self.tracer.start_span("langchain_chain")
        self.span.set_attribute("input_keys", list(inputs.keys()))
        self.span.set_attribute("input_size", sum(len(str(v)) for v in inputs.values()))

    def on_chain_end(self, outputs, **kwargs):
        self.span.set_attribute("output_keys", list(outputs.keys()))
        self.span.set_attribute("output_size", sum(len(str(v)) for v in outputs.values()))
        self.span.end()

    def on_chain_error(self, error, **kwargs):
        self.span.record_exception(error)
        self.span.set_attribute("error", True)
        self.span.end()
