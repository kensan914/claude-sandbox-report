FROM oven/bun:1-debian

WORKDIR /app

# Install dependencies first for better caching
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Copy application code
COPY . .

EXPOSE 3000

CMD ["bun", "run", "dev", "--hostname", "0.0.0.0"]
