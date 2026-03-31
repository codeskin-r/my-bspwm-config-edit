#!/bin/bash
iso="$1"
loopdev=$(sudo losetup --find --show "$iso")
udisksctl mount -b "$loopdev"
