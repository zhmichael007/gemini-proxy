import uvicorn,json,yaml
from fastapi import FastAPI, Header, HTTPException, Body
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

# 定义一个模型用于接收 JSON 数据
class RequestData(BaseModel):
    model: str = None
    prompt: str = None

app = FastAPI()

generation_config = {
    "temperature": 0.5,
    "top_p": 1,
}

project_id = ""
region="us-central1"
temp=0.5
master_key=""

with open('/config/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    project_id=config["gemini_proxy_settings"]["vertex_project"]
    region=config["gemini_proxy_settings"]["vertex_location"]
    generation_config["temperature"]=config["gemini_proxy_settings"]["temperature"]
    master_key=config["gemini_proxy_settings"]["master_key"]
    print(f'project id: {project_id}, region: {region}, temperature: {generation_config["temperature"]}, master_key: {master_key[0:2]}......')

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/prompt")
async def create_prompt(data: RequestData = Body(...), authorization: Optional[str] = Header(None)):
    # 检查 Authorization 头是否存在
    if authorization is None:
        raise HTTPException(status_code=400, detail="Authorization header is missing")
    
    # 检查 Authorization 头的类型
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization type. Must be 'Bearer'")
    
    # 提取令牌值
    token = authorization.split("Bearer ")[1].strip()
    if token != master_key:
        raise HTTPException(status_code=400, detail="master key is not right")

    # 检查 model 和 prompt 字段是否为空
    if not data.model or not data.model.strip():
        raise HTTPException(status_code=400, detail="model is missing or empty")
    if not data.prompt or not data.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is missing or empty")

    vertexai.init(project=project_id, location=region)
    model = GenerativeModel(data.model.strip())
    try:
        response = model.generate_content(
            data.prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        return response.text
    except Exception as e:
        print("An error occurred:", e)
        raise HTTPException(status_code=500, detail=e.message)

if __name__ == '__main__':
    uvicorn.run(app=app, host="0.0.0.0", port=4000)