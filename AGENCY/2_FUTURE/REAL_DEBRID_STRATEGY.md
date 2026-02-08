# 🚀 ESTRATEGIA DE INTEGRACIÓN: REAL-DEBRID (RD)

Real-Debrid actuará como nuestra **"Capa de Gratificación Instantánea"**. No sustituye a Radarr (que es el curador), sino que lo potencia.

## 📅 FASE 1: La Base "Collector" (Implementada)
*   **Funcionamiento**: Radarr busca torrents latinos -> Los baja a tu disco/nube.
*   **Ventaja**: Tienes el archivo para siempre, en la máxima calidad, sin depender de ninguna suscripción externa una vez descargado.

## 📅 FASE 2: Turbo-Downloader (RD como Cliente de Descarga)
*   **Objetivo**: Eliminar la necesidad de "Seeders" y VPN de descarga.
*   **Implementación**: Añadir **RDT-Client** al `docker-compose.yml`.
*   **Funcionamiento**: RD descarga a 10Gbps y tu servidor lo baja como descarga directa.

## 📅 FASE 3: El Paradigma "Gelato" (VOD Instantáneo)
*   **Objetivo**: Ver contenido sin descargarlo, estilo Netflix puro.
*   **Implementación**: Plugin **Gelato** en Jellyfin.
*   **Funcionamiento**: Streaming directo desde el caché de RD.

## 📅 FASE 4: Automatización de "Caché Latino"
*   **Objetivo**: Asegurar que lo que hay en RD sea Latino mediante scripts de inyección.
