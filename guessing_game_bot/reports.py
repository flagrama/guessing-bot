"""Contains the Reports class."""
import os.path
import errno
import csv
from datetime import datetime
import boto3

class Reports():
    """Writes report CSVs and uploads them to S3."""

    def __init__(self):
        self.filename = str(datetime.now()).replace(':', '_')

    def write_guess_report(self, log):
        """Writes the guessing log report CSV then uploads it to S3.

        Arguments:
            log {deque} -- A queue of all the guesses made during a guessing game
        """

        file = os.path.join(os.path.curdir, 'reports', '%s.csv' % self.filename)
        if not os.path.exists(file):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        report_writer = csv.writer(open(file, 'w', newline=''))
        report_writer.writerow(
            ["Timestamp", "Participant ID", "Participant Username", "Guess Type",
             "Item", "Current Session Points", "Total Session Points"])
        for guess in log:
            report_writer.writerow(
                [guess['timestamp'], guess['participant'], guess['participant_name'],
                 guess['guess_type'], guess['guess'], guess['session_points'],
                 guess['total_points']])
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            amazon_s3 = boto3.resource('s3')
            bucket = amazon_s3.Bucket(os.environ['S3_BUCKET'])
            bucket.upload_file(file, str(datetime.now()) + '.csv', ExtraArgs={'ACL':'public-read'})

    def write_totals_report(self, participants):
        """Writes the totals report CSV then uploads it to S3.

        Arguments:
            participants {list} -- A list of all the participants a streamer has
        """

        file = os.path.join(os.path.curdir, 'reports', '%s totals.csv' % self.filename)
        if not os.path.exists(file):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        report_writer = csv.writer(
            open(file, 'w', newline=''))
        report_writer.writerow(["Participant ID", "Participant Username", "Total Points"])
        for participant in participants:
            report_writer.writerow([participant.user_id, participant.username,
                                    participant.total_points])
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            amazon_s3 = boto3.resource('s3')
            bucket = amazon_s3.Bucket(os.environ('S3_BUCKET'))
            bucket.upload_file(file, str(datetime.now()) + '.csv', ExtraArgs={'ACL':'public-read'})
