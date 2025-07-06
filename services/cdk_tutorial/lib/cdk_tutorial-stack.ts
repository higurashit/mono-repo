import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codecommit from 'aws-cdk-lib/aws-codecommit';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import { Construct } from 'constructs';

export class CdkTutorialStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const accountId = cdk.Stack.of(this).account; // AWSアカウントID

    new s3.Bucket(this, 'MyBucket', {
      bucketName: `my-cdk-app-bucket-${accountId}`,
      versioned: true, // バージョニングを有効化
      removalPolicy: cdk.RemovalPolicy.DESTROY, // スタック削除時にバケットを削除
      autoDeleteObjects: true, // バケット削除時に中身を削除
    });

    const sourceArtifact = new codepipeline.Artifact();
    const buildArtifact = new codepipeline.Artifact();

    const pipeline = new codepipeline.Pipeline(this, 'MyPipeline', {
      pipelineName: 'MyCdkPipeline',
    });

    const sourceStage = pipeline.addStage({
      stageName: 'Source',
      actions: [
        new codepipeline_actions.CodeCommitSourceAction({
          actionName: 'CodeCommit',
          repository: new codecommit.Repository(this, 'MyRepo', {
            repositoryName: 'my-cdk-repo',
          }),
          output: sourceArtifact,
        }),
      ],
    });

    const buildStage = pipeline.addStage({
      stageName: 'Build',
      actions: [
        new codepipeline_actions.CodeBuildAction({
          actionName: 'CodeBuild',
          project: new codebuild.PipelineProject(this, 'MyBuildProject'),
          input: sourceArtifact,
          outputs: [buildArtifact],
        }),
      ],
    });

    pipeline.addStage({
      stageName: 'Deploy',
      actions: [
        new codepipeline_actions.CloudFormationCreateUpdateStackAction({
          actionName: 'DeployStack',
          stackName: 'MyCdkAppStack',
          templatePath: buildArtifact.atPath('template.yaml'),
          adminPermissions: true,
        }),
      ],
    });
  }
}
