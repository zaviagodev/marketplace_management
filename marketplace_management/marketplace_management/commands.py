import click
import frappe
from frappe.utils.background_jobs import get_queue_list
from poll_marketplace_events import poll_marketplace_events


@click.command("set-polling")
@click.argument("state", type=click.Choice(["on", "off"]))
@click.argument("queue-url", type=str)
@click.argument("aws-access-key-id", type=str)
@click.argument("aws-secret-access-key", type=str)
@click.argument("region-name", type=str)
@click.option("--queue", default="marketplaceEventsQueue")
def set_polling(
    state, queue_url, aws_access_key_id, aws_secret_access_key, region_name, queue
):
    if state == "on":
        frappe.enqueue(
            poll_marketplace_events,
            queue_url=queue_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            queue=queue,
        )
    else:
        queue_list = get_queue_list()
        click.echo(f"Queue list: {queue_list}")
