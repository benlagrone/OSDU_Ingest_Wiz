from retry_decorator import async_retry
from progress_tracker import ProgressTracker
from logger import ingestion_logger, error_logger
import aiohttp
import asyncio
import json
from azure.storage.blob.aio import BlobServiceClient

class ADMEIngestionClient:
    def __init__(self, config):
        self.adme_endpoint = config['adme_endpoint']
        self.credentials = config['adme_credentials']
        self.max_concurrent_uploads = config['max_concurrent_uploads']
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @async_retry(max_attempts=3, delay=5)
    async def upload_to_adme(self, file_content, manifest):
        try:
            # This is a placeholder. Replace with actual ADME API call
            async with self.session.post(
                f"{self.adme_endpoint}/ingest",
                json={"manifest": manifest, "content": file_content.decode()},
                headers={"Authorization": f"Bearer {self.credentials['access_token']}"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_msg = await response.text()
                    raise Exception(f"ADME API error: {response.status} - {error_msg}")
        except Exception as e:
            error_logger.error(f"Error uploading to ADME: {str(e)}")
            raise

async def ingest_to_adme(config, manifests_file):
    with open(manifests_file, 'r') as f:
        manifests = json.load(f)

    async with ADMEIngestionClient(config) as adme_client:
        progress_tracker = ProgressTracker(len(manifests))
        semaphore = asyncio.Semaphore(config['max_concurrent_uploads'])

        async def process_file(blob, manifest):
            try:
                async with semaphore:
                    file_content = await blob.download_blob().readall()
                    result = await adme_client.upload_to_adme(file_content, manifest)
                    ingestion_logger.info(f"Successfully ingested {blob.name}")
                    progress_tracker.update(1)
                    return result
            except Exception as e:
                error_logger.error(f"Failed to ingest {blob.name}: {str(e)}")
                return None

        blob_service_client = BlobServiceClient.from_connection_string(config['connection_string'])
        container_client = blob_service_client.get_container_client(config['container_name'])

        tasks = []
        async for blob in container_client.list_blobs():
            if blob.name in manifests:
                task = asyncio.create_task(process_file(blob, manifests[blob.name]))
                tasks.append(task)

        results = await asyncio.gather(*tasks)
        progress_tracker.complete()

        return results
