# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json

from os import path
from typing import Any
import os.path
from aws_cdk import core
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.core import Duration, RemovalPolicy, Stack
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_iam as iam

from aws_cdk.custom_resources import Provider


class ConnectStreamingResource(core.Construct):
    """S3 Object constructs that uses AWSCustomResource internally
    Arguments:
        :param instance_id -- ARN of Connect Instance
        :parm resource_type -- "CONTACT_TRACE_RECORDS" or "AGENT_EVENTS" << only KINESIS is valid storage type for AGent Events
        :param storage_type -- KINESIS_FIREHOSE OR  KINESIS_STREAM
        :param kinesis_arn -- Firehose or Kinesis Arn
    """
    def __init__(self, scope: core.Construct, id: str, 
            instance_id: str, 
            resource_type: str, 
            storage_type: str, 
            kinesis_arn: str, 
            log_retention=None)  -> None:
        super().__init__(scope, id)

        account_id = Stack.of(self).account
        region = Stack.of(self).region

        # IMPORTANT! Setting resources to the exact policy name is the most restrictive y
        # Which is more permissive.
        lambda_role = iam.Role(
            scope=self,
            id=f'{id}LambdaRole',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "ConnectStreamingProvisioningPolicy":
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                            ],
                            resources=[
                                f'arn:aws:logs:{region}:{account_id}:*'
                            ],
                            effect=iam.Effect.ALLOW,
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=[
                                f'arn:aws:logs:{region}:{account_id}:log-group:*'
                            ],
                            effect=iam.Effect.ALLOW,
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "iam:PutRolePolicy"
                            ],
                            resources=[
                                '*'
                            ],
                            effect=iam.Effect.ALLOW,
                        )
                    ])
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                ,iam.ManagedPolicy.from_aws_managed_policy_name("AmazonConnect_FullAccess")
            ],
        )

        
        timeout = Duration.minutes(5)

        
        dirname = os.path.dirname(__file__)

        event_handler = aws_lambda.Function(
            scope=self,
            id=f'{id}EventHandler',
            runtime= aws_lambda.Runtime.NODEJS_14_X,
            code= aws_lambda.Code.from_asset(os.path.join(dirname, 'lambda_js_code')),
            handler='index.handler',
            role=lambda_role,
            timeout=timeout,
        )

        provider = Provider(scope=self, 
                            id=f'{id}Provider', 
                            on_event_handler=event_handler,
                            log_retention = RetentionDays.ONE_DAY)

        core.CustomResource(
            scope=self,
            id=f'{id}ConnectPolicy',
            service_token=provider.service_token,
            removal_policy=RemovalPolicy.DESTROY,
            resource_type="Custom::AssociateStreamWithConnect",
            properties={
                "instance_id": instance_id,
                "resource_type": resource_type,
                "storage_type": storage_type,
                "kinesis_arn": kinesis_arn
            },
        )
