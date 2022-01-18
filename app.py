# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3

from aws_cdk import core

from connect_cdk.connect_cdk_stack import ConnectCdkStack
from custom_rsrcs_cdk.custom_rsrcs_stack import CustomResourceConnectStreaming


app = core.App()

ConnectCdkStack(app, "connect-cdk")

app.synth()
