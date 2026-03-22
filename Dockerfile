FROM python:3.12-slim

# Install Firefox and dependencies for headless browsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    firefox-esr \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN GECKODRIVER_VERSION=$(wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest \
    | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/') \
    && wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper/ scraper/
RUN mkdir -p /data
RUN printf 'SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n0 */12 * * * root cd /app && /usr/local/bin/python -m scraper.main -c scraper/config.yml >> /proc/1/fd/1 2>> /proc/1/fd/2\n' > /etc/cron.d/price-tracker \
    && chmod 0644 /etc/cron.d/price-tracker

CMD ["cron", "-f"]
