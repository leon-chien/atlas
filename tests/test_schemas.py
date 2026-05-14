from __future__ import annotations

from atlas.core.schemas import (
    CameraIntrinsics,
    CameraPose,
    FrameRecord,
    ObjectNode,
    ObjectObservation,
    RelationEdge,
    SceneGraph,
    StageManifest,
    StageStatus,
    Trajectory,
    VideoMetadata,
)


def test_schema_json_round_trips():
    video = VideoMetadata(
        source_video="input/source_video.mp4",
        frame_count=300,
        fps=30,
        duration_s=10,
        width=1920,
        height=1080,
    )
    assert VideoMetadata.model_validate_json(video.model_dump_json()) == video

    frame = FrameRecord(
        frame_id="frame_000001",
        timestamp_s=0.0,
        path="frames/frame_000001.jpg",
        blur_score=12.5,
        width=640,
        height=480,
    )
    assert FrameRecord.model_validate_json(frame.model_dump_json()) == frame

    intrinsics = CameraIntrinsics(fx=500, fy=500, cx=320, cy=240, width=640, height=480)
    pose = CameraPose(
        frame_id=frame.frame_id,
        intrinsics=intrinsics,
        world_to_camera=[
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        confidence=0.95,
    )
    assert CameraPose.model_validate_json(pose.model_dump_json()) == pose

    observation = ObjectObservation(
        frame_id=frame.frame_id,
        label="desk",
        bbox_xyxy=[1, 2, 10, 20],
        mask_path="semantics/masks/frame_000001_desk.png",
        score=0.9,
        embedding_id="embedding_001",
    )
    assert ObjectObservation.model_validate_json(observation.model_dump_json()) == observation

    node = ObjectNode(
        object_id="desk_001",
        label="desk",
        centroid_3d=[0, 0, 0],
        bbox_3d=[-1, -1, -1, 1, 1, 1],
        visible_frames=[frame.frame_id],
    )
    assert ObjectNode.model_validate_json(node.model_dump_json()) == node

    edge = RelationEdge(source="desk_001", target="laptop_001", relation="supports", confidence=0.8)
    assert RelationEdge.model_validate_json(edge.model_dump_json()) == edge

    graph = SceneGraph(graph_id="scan_graph", objects=[node], relations=[edge])
    assert SceneGraph.model_validate_json(graph.model_dump_json()) == graph

    trajectory = Trajectory(trajectory_id="walk_left", poses=[pose])
    assert Trajectory.model_validate_json(trajectory.model_dump_json()) == trajectory

    manifest = StageManifest(
        stage_name="ingest",
        backend="opencv",
        inputs=["input/source_video.mp4"],
        outputs=["metadata/video.json", "metadata/frames.json"],
        status=StageStatus.complete,
    )
    assert StageManifest.model_validate_json(manifest.model_dump_json()) == manifest
