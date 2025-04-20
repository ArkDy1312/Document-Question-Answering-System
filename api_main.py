from fastapi import FastAPI
import os
from app.api.routes import router as main_router
from app.api.auth import auth_router
from prometheus_fastapi_instrumentator import Instrumentator
# 🚀 Add OpenTelemetry FastAPI auto-instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace
# from app.api.admin import router as admin_router
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates



# --- Setup tracing ---
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "document-qa-api"}))
)

OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317/v1/traces")
otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Register routes
app = FastAPI(title="Document QA API")
app.include_router(auth_router)
app.include_router(main_router)
# app.include_router(admin_router)

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

# Instrument FastAPI + Requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)
