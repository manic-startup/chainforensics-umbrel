# ChainForensics Frontend - Static HTML served by nginx
# Umbrel-compatible Dockerfile
FROM nginx:1.25-alpine

# Copy static files
COPY public/ /usr/share/nginx/html/

# Copy nginx config template for envsubst
COPY nginx.conf /etc/nginx/templates/default.conf.template

# nginx:alpine uses envsubst for environment variable substitution in templates
# This allows ${APP_CHAINFORENSICS_API_IP} to be resolved at runtime
# The template is processed and output to /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
