#!/bin/sh

BACKUP_SOURCE={{ p4_root }}
S3BUCKET={{ s3_bucket }}
ARCHIVEPREFIX={{ server_host }}_repo_
S3CMD=s3cmd
TMPDIR=/tmp

ARCHIVEFILE=$ARCHIVEPREFIX$(date +"%m_%d_%Y_%H_%M").tar.gz

tar zcvf $TMPDIR/$ARCHIVEFILE $BACKUP_SOURCE

$S3CMD put --progress $TMPDIR/$ARCHIVEFILE s3://$S3BUCKET/$ARCHIVEFILE

rm $TMPDIR/$ARCHIVEFILE

#tar zcvf - $BACKUP_SOURCE | $S3CMD put --progress - s3://$S3BUCKET/$ARCHIVEFILE
