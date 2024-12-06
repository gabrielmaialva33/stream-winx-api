import logging

from locust import HttpUser, task, between, SequentialTaskSet


class APITests(SequentialTaskSet):

    @task
    def paginate_posts(self):
        """Testa a paginação de posts."""
        with self.client.get(
            "/api/v1/posts",
            params={"per_page": 10, "offset_id": 0},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info("Paginação de posts sucedida.")
            else:
                logging.error(
                    f"Falha na paginação de posts: {response.status_code}, {response.text}"
                )
                response.failure(f"Erro ao paginar posts: {response.status_code}")

    @task
    def get_image(self):
        """Testa a obtenção de uma imagem específica."""
        message_id = 7188  # Use o ID de uma mensagem existente
        with self.client.get(
            f"/api/v1/posts/images/{message_id}", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info(f"Imagem com message_id={message_id} obtida com sucesso.")
            else:
                logging.error(
                    f"Falha ao obter imagem: {response.status_code}, {response.text}"
                )
                response.failure(f"Falha ao obter imagem: {response.status_code}")

    @task
    def stream_video(self):
        """Testa o streaming de vídeo."""
        message_id = 7189  # Use o ID de uma mensagem existente
        document_id = 5044457385712682420  # Exemplo de documentId
        size = 3988488346  # Exemplo de tamanho de documento
        headers = {"Range": f"bytes={size - 100}-{size}"}

        with self.client.get(
            f"/api/v1/posts/stream",
            params={"message_id": message_id, "document_id": document_id, "size": size},
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code == 206:
                response.success()
                logging.info("Streaming de vídeo obtido com sucesso.")
            else:
                logging.error(
                    f"Falha no streaming de vídeo: {response.status_code}, {response.text}"
                )
                response.failure(f"Erro no streaming de vídeo: {response.status_code}")

    @task
    def get_post(self):
        """Testa a obtenção de um post específico."""
        message_id = 7188  # Use o ID de uma mensagem existente
        with self.client.get(
            f"/api/v1/posts/{message_id}",
            headers={"Accept": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info(f"Post com message_id={message_id} obtido com sucesso.")
            else:
                logging.error(
                    f"Falha ao obter post: {response.status_code}, {response.text}"
                )
                response.failure(f"Erro ao obter post: {response.status_code}")


class WebsiteUser(HttpUser):
    tasks = [APITests]
    wait_time = between(1, 5)  # Intervalo de espera entre execuções das tarefas
