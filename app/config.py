from transformers import pipeline as hf_pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace

def get_llm(type: str) -> HuggingFacePipeline:
    """
    Get the LLM pipeline based on the type.
    Args:
        type (str): The type of LLM to get. Options are "summarizer" or "qa".
    Returns:
        HuggingFacePipeline: The LLM pipeline.
    """
    if type == "summarizer":
        # Use a lightweight, high-quality summarizer
        summarizer = hf_pipeline(
            "summarization",
            model="teapotai/teapotllm", #"google/pegasus-xsum",  # small + accurate
            max_length=100,
            min_length=30,
            do_sample=False)
        llm = HuggingFacePipeline(pipeline=summarizer)
        return ChatHuggingFace(llm=llm, verbose=True)
    elif type == "qa":
        model_name = "teapotai/teapotllm"
        pipe = hf_pipeline(  
            "text2text-generation",
            model=model_name,
            tokenizer=model_name,
            device=0,
            max_new_tokens=512,
            do_sample=False,
            repetition_penalty=1.03,
            # temperature=0.1
        )
        return HuggingFacePipeline(pipeline=pipe)
    
