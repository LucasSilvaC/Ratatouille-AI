FROM python:3.14-slim AS api
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=docker_settings
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/manage.py .
COPY apps/api/apps ./apps
COPY apps/api/project ./project
COPY infra/docker/django_settings.py ./docker_settings.py
COPY infra/docker/start-api.sh /usr/local/bin/start-api
COPY infra/database/db.sqlite /seed/db.sqlite
RUN useradd --create-home --uid 1001 django \
    && install -d -o django /data \
    && python manage.py collectstatic --noinput
USER django
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/usr/local/bin/start-api"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]

FROM node:26.13.1-alpine AS base
WORKDIR /app
RUN npm install -g pnpm@11.10.0

FROM base AS dependencies
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
RUN pnpm install --frozen-lockfile

FROM dependencies AS migrator
COPY . .
CMD ["pnpm", "db:migrate"]

FROM dependencies AS builder
ARG NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV NEXT_PUBLIC_APP_URL=${NEXT_PUBLIC_APP_URL}
COPY . .
RUN pnpm build

FROM node:26.13.1-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public
USER nextjs
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
