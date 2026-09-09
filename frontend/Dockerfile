FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# ✅ Aseguramos que el contenedor exponga el puerto 5173
EXPOSE 5173

# ✅ Forzamos a Vue CLI a usar el puerto 5173 y escuchar en 0.0.0.0
CMD ["npm", "run", "serve", "--", "--port", "5173", "--host", "0.0.0.0"]
