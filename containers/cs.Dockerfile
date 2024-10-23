FROM mcr.microsoft.com/dotnet/sdk:6.0

RUN apt update && apt install -y --no-install-recommends --no-install-suggests python3
