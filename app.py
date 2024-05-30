# azure SDK を使用して，Azure VMを起動する
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import os
import json

# 設定jsonファイルの読み込み
with open("settings.json", "r") as f:
    config = json.load(f)

# discord botの設定
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
guild = discord.Object(id=config["guild_id"])

############################################################################################################

# VMを起動する関数
async def powerOn(subcription_id, resource_group, vm_name):
    # azure 認証を取得
    credential = DefaultAzureCredential()

    # ComputeManagementClient インスタンスを作成
    compute_client = ComputeManagementClient(credential, subcription_id)

    # VMの起動を非同期で実行
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lambda: compute_client.virtual_machines.begin_start(resource_group, vm_name))

    # 非同期で待機
    await loop.run_in_executor(None, result.wait)


# VMを停止する関数
async def powerOff(subcription_id, resource_group, vm_name):
    # azure 認証を取得
    credential = DefaultAzureCredential()

    # ComputeManagementClient インスタンスを作成
    compute_client = ComputeManagementClient(credential, subcription_id)

    # VMの停止を非同期で実行
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lambda: compute_client.virtual_machines.begin_deallocate(resource_group, vm_name))
    
    # 非同期で待機
    await loop.run_in_executor(None, result.wait)

# サーバーの状態を取得する関数
def getResponse(url):
    response = requests.get(url)
    jsonData = response.json()
    return jsonData

############################################################################################################

# サーバーの起動
@tree.command(name = "startvm", description = "仮想マシンを起動します")
@app_commands.guilds(guild)
async def startVM(interaction: discord.Interaction):
    # defer
    await interaction.response.defer()

    # VMを起動
    await powerOn(config["subscription_id"], config["resource_group"], config["vm_name"])

    embed = discord.Embed( # Embedを定義する
        title="仮想マシンを起動しました",# タイトル
        color=0x00ff00, # フレーム色指定(今回は緑)
        description="" # Embedの説明文 必要に応じて
    )
    await interaction.followup.send(embed=embed) # Embedを送信

# サーバーの停止
@tree.command(name = "stopvm", description = "仮想マシンを停止します")
@app_commands.guilds(guild)
async def stopVM(interaction: discord.Interaction):
    # defer
    await interaction.response.defer()

    #VMを停止
    await powerOff(config["subscription_id"], config["resource_group"], config["vm_name"])

    embed = discord.Embed( # Embedを定義する
        title="仮想マシンを停止しました",# タイトル
        color=0xff0000, # フレーム色指定(今回は赤)
        description="" # Embedの説明文 必要に応じて
    )
    await interaction.followup.send("embed=embed") # Embedを送信

@client.event
async def on_ready():
    await tree.sync(guild=guild)

token = os.getenv("BOT_TOKEN")
client.run(token)