import click
import frappe
from rq.command import send_stop_job_command
from rq.exceptions import InvalidJobOperation
from frappe.utils.background_jobs import get_redis_conn
from frappe.commands import get_site

from marketplace_management.poll_marketplace_events import poll_marketplace_events


@click.command("marketplace-polling")
@click.argument("state", default="on", type=click.Choice(["on", "off"]))
@click.option("--site", help="site name")
@click.option("--queue-url", type=str, help="AWS SQS Queue URL")
@click.option("--aws-access-key-id", type=str, help="AWS Access Key ID")
@click.option("--aws-secret-access-key", type=str, help="AWS Key Secret")
@click.option("--region", type=str, help="AWS Region")
@click.option("--queue", default="marketplaceEventsQueue")
@click.pass_context
def marketplace_polling(context, site, queue_url, aws_access_key_id, aws_secret_access_key, region, queue, state):
    site = site or get_site(context)
    frappe.init(site=site)
    frappe.connect()
    if state == "on":
        # validate
        missing_args = []
        if not queue_url:
            missing_args.append("--queue-url")
        if not aws_access_key_id:
            missing_args.append("--aws-access-key-id")
        if not aws_secret_access_key:
            missing_args.append("--aws-secret-access-key")
        if not region:
            missing_args.append("--region")
        
        if missing_args:
            click.echo(f"Missing required arguments: {', '.join(missing_args)}")
            return

        # start job
        frappe.enqueue(
            poll_marketplace_events,
            queue_url=queue_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region,
            queue=queue,
            job_id="poll_marketplace_events",
            deduplicate=True
        )
    else:
        job_name = f"{site}::poll_marketplace_events"
        click.echo(f"Stopping job {job_name}")
        try:
            send_stop_job_command(connection=get_redis_conn(), job_id=job_name)
        except InvalidJobOperation:
            click.echo(f"Job {job_name} is not running.")
        


commands = [
    marketplace_polling
]