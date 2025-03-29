FROM nginx:1.27.4-alpine-slim
ENV NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template
