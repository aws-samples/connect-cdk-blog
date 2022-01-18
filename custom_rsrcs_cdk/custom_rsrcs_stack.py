# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    core,
)

from custom_rsrcs_cdk.connect_streaming_custom import ConnectStreamingResource
import logging


class CustomResourceConnectStreaming(core.NestedStack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        instance_id: str, 
        ctr_stream_type: str, 
        ctr_stream_arn: str, 
        agent_stream_arn: str, 
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        CTRConnection = ConnectStreamingResource(scope=self, id="ConnectCTRStreamingSetup", 
            instance_id=instance_id, 
            resource_type="CONTACT_TRACE_RECORDS", 
            storage_type= ctr_stream_type, 
            kinesis_arn= ctr_stream_arn)

        AgentConnection = ConnectStreamingResource(scope=self, id="ConnectAgentStreamingSetup", 
            instance_id=instance_id, 
            resource_type="AGENT_EVENTS", 
            storage_type="KINESIS_STREAM", 
            kinesis_arn=agent_stream_arn)

        core.CfnOutput(self, "Received Instance_id", value= instance_id)
        core.CfnOutput(self, "Received ctr_stream_type", value=ctr_stream_type)
        core.CfnOutput(self, "Received ctr_stream_arn", value= ctr_stream_arn)
        core.CfnOutput(self, "Received agent_stream_arn", value=agent_stream_arn)
      