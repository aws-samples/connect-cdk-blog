# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_kinesis as _kinesis,
    aws_kinesisfirehose as _firehose,
    aws_s3 as _s3,
    aws_iam as _iam,
    core)

# from connect_streaming_custom import ConnectStreamingResource
import logging

from custom_rsrcs_cdk.custom_rsrcs_stack import CustomResourceConnectStreaming

# s3_bucket_name = "cdk-demo-connect-tmak"
class ConnectCdkStack(core.Stack):

    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        connect_instance_id = core.CfnParameter(self, "instanceId", type="String",
            description="Amazon Connect InstanceID in format 2dg7a79f-94ed-4cbc-9217-f66id1e87424.")

        ctr_stream_name = core.CfnParameter(self, "ctrStreamName", type="String",
            description="Contact Trace Records Kinesis Stream Name.",
            default="CRTStreamForConnect")

        agent_events_stream_name = core.CfnParameter(self, "agentStreamName", type="String",
            description="Contact Trace Records Kinesis Stream Name.",
            default="AgentStreamForConnect")

        # Base Resources stack
        baseResources = BaseResources(self, "baseResources", 
            connect_instance_id = connect_instance_id,
            ctr_stream_name = ctr_stream_name,
            agent_events_stream_name = agent_events_stream_name)

            # Stack that connects streams and Amazon Connect streaming
        connect_streaming_stack = CustomResourceConnectStreaming(self,
            "connect_streaming_stack",
            instance_id = baseResources.instance_id,
            ctr_stream_type =baseResources.ctr_stream_type,
            ctr_stream_arn = baseResources.ctr_stream_arn,
            agent_stream_arn = baseResources.agent_stream_arn
        )

        connect_streaming_stack.node.add_dependency(baseResources)        
        
        #AgentConnection = ConnectStreamingResource(scope=self, id="ConnectAgentStreamingSetup", 
        #    instance_id=connect_instance_arn, 
        #    resource_type="AGENT_EVENTS", 
        #    storage_type="KINESIS_STREAM", 
        #    kinesis_arn=kinesis_input_stream_agnt.stream_arn)

class BaseResources(core.NestedStack):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    def __init__(self, scope: core.Construct, construct_id: str, 
        connect_instance_id: str,
        ctr_stream_name : str,
        agent_events_stream_name: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        connect_iam_role = _iam.Role(self, "connectIamRole",
                                assumed_by = _iam.AccountPrincipal(core.Aws.ACCOUNT_ID),
                                description="IAM role for records to access AWS services.",
                                role_name="connectIamRole"
                            )
        
        # Adding connect access to IAM role.
        connect_iam_role.add_to_policy(
            _iam.PolicyStatement(
                resources=['*'],
                actions=[
                    "connect:*"
                ]
            )
        )

        # defined in cdk.json
        streamType = self.node.try_get_context("ctr_stream_type")
        logging.debug(f'Evaluated yetAnother is {streamType}')
      
        ctrStreamArn = ""
        storageType = ""
    
        if streamType == "KINESIS_FIREHOSE":
            # we need S3 bucket 
            s3BucketName = "agent-data-" + self.region +"-"+ self.account 
            s3_bucket = _s3.Bucket(self, "connectOutputBucketS3", 
                bucket_name= s3BucketName,
                removal_policy= core.RemovalPolicy.DESTROY
            )


            firehose_role = _iam.Role(self, "firehose-role", assumed_by=_iam.ServicePrincipal("firehose.amazonaws.com"))
            firehose_role_arn = firehose_role.role_arn
            kinesis_input_stream_ctr = _firehose.CfnDeliveryStream(
                self,"kinesisCTRStream",
                delivery_stream_name= ctr_stream_name.value_as_string, 
                delivery_stream_type="DirectPut",
                s3_destination_configuration=_firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn=s3_bucket.bucket_arn,
                    buffering_hints=_firehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=60
                    ),
                compression_format="UNCOMPRESSED",
                role_arn=firehose_role_arn
                )
            )
            
            # set the valuse needed by Connect custom resource
            core.Stack.of(self).account
            ctrStreamArn = "arn:aws:firehose:" +self.region +":"+ self.account +":deliverystream/"+ ctr_stream_name.value_as_string
            #ctrStreamArn = "arn:aws:firehose:" + core.Stack.of(self).region +":"+core.Stack.of(self).account+ ":deliverystream/" + ctr_stream_name.value_as_string;
            storageType = "KINESIS_FIREHOSE"
            

        else:
            # Defining-creating Connect CTR Kinesis stream.
            kinesis_input_stream_ctr = _kinesis.Stream(self, "kinesisCTRStream",
                                    stream_name=ctr_stream_name.value_as_string
                                )
            kinesis_input_stream_ctr.grant_write(connect_iam_role)
            # set the valuse needed by Connect custom resource
            ctrStreamArn = kinesis_input_stream_ctr.stream_arn
            storageType = "KINESIS_STREAM"

        core.CfnOutput(self, "CTR Stream ARN", value= ctrStreamArn)
        logging.debug(f'Stream ARN is {ctrStreamArn}')
        # Defining-creating  Agent Events Kinesis stream.
        kinesis_input_stream_agnt = _kinesis.Stream(self, "kinesisAgentStream",
                                    stream_name=agent_events_stream_name.value_as_string
                                )
        ## give Connect Role permissions to write to Kinesis streams
        kinesis_input_stream_agnt.grant_write(connect_iam_role)
        
        # outputs
        core.CfnOutput(self, "Agent StreamARN", value= kinesis_input_stream_agnt.stream_arn)
        core.CfnOutput(self, "CTR Stream Type Parm (from cdk.json)", value= streamType)
        
        # Full Connect Instance ARN
        connect_instance_arn =  "arn:aws:connect:" + self.region +":" + self.account + ":instance/" + connect_instance_id.value_as_string
        logging.debug(f'Connect Instance ARN {connect_instance_arn}')
        
        core.CfnOutput(self, "ConnectInstanceARN", value= connect_instance_arn)
        core.CfnOutput(self, "StorageType", value=storageType)

        self.instance_id = connect_instance_id.value_as_string
        self.ctr_stream_type =  streamType
        self.ctr_stream_arn = ctrStreamArn 
        self.agent_stream_arn = kinesis_input_stream_agnt.stream_arn 
