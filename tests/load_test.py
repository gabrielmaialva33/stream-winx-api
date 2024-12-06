import logging

from locust import HttpUser, task, between, SequentialTaskSet


class APITests(SequentialTaskSet):

    @task
    def paginate_posts(self):
        with self.client.get(
                "/api/v1/posts",
                params={"per_page": 10, "offset_id": 0},
                catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info(f"Paginating posts successfully.")
            else:
                logging.error(f"Erro on posts pagination: {response.status_code} {response.text}")
                response.failure(f"Error while paginating posts: {response.status_code}")

    @task
    def get_image(self):
        message_id = 7188
        with self.client.get(
                f"/api/v1/posts/images/{message_id}", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info(f"Image with message_id={message_id} obtained successfully.")
            else:
                logging.error(f"Failure to get image: {response.status_code}")
                response.failure(f"Error while getting image: {response.status_code}")

    @task
    def stream_video(self):
        message_id = 7189
        document_id = 5044457385712682420
        size = 3988488346
        headers = {"Range": f"bytes={size - 100}-{size}"}

        with self.client.get(
                f"/api/v1/posts/stream",
                params={"message_id": message_id, "document_id": document_id, "size": size},
                headers=headers,
                catch_response=True,
        ) as response:
            if response.status_code == 206:
                response.success()
                logging.info(f"Sucessefully streamed video")
            else:
                logging.error(f"Erro on video streaming: {response.status_code} {response.text}")
                response.failure(f"Erro no streaming de vídeo: {response.status_code}")

    @task
    def get_post(self):
        message_id = 7188
        with self.client.get(
                f"/api/v1/posts/{message_id}",
                headers={"Accept": "application/json"},
                catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                logging.info(f"Post with message_id={message_id} obtained successfully.")
            else:
                logging.error(f"An error occurred while getting post: {response.status_code}")
                response.failure(f"Error while getting post: {response.status_code}")


class WebsiteUser(HttpUser):
    tasks = [APITests]
    wait_time = between(1, 5)
