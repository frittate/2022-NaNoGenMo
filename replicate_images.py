import replicate

CLIENT = replicate.Client(api_token="48743e2e94ca24c5016954a617ac5830333afd21")
model = CLIENT.models.get("stability-ai/stable-diffusion")
link = model.predict(prompt="INT. SEAN'S APARTMENT -- NIGHT", width=256, height=256)
print(link)