import subprocess

from fastapi import APIRouter, Depends, HTTPException

from app.k8s.client import K8sClient
from app.schemas.node import NodeDetail, NodeJoinRequest, NodeJoinResponse, NodeSummary
from app.services.node_service import NodeService

router = APIRouter(prefix="/nodes", tags=["nodes"])


def get_node_service() -> NodeService:
    return NodeService(K8sClient())


@router.get("", response_model=list[NodeSummary])
async def list_nodes(service: NodeService = Depends(get_node_service)):
    return service.list_nodes()


@router.get("/{name}", response_model=NodeDetail)
async def get_node(name: str, service: NodeService = Depends(get_node_service)):
    node = service.get_node(name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{name}' not found")
    return node


@router.post("/join", response_model=NodeJoinResponse)
async def join_node(
    request: NodeJoinRequest,
    service: NodeService = Depends(get_node_service),
):
    cmd = service.get_join_command(request)
    return NodeJoinResponse(
        success=True,
        message=f"Run the following command to join {request.host}",
        join_command=cmd,
    )


@router.delete("/{name}")
async def drain_node(name: str, service: NodeService = Depends(get_node_service)):
    node = service.get_node(name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{name}' not found")
    try:
        subprocess.run(
            ["kubectl", "drain", name, "--ignore-daemonsets", "--delete-emptydir-data"],
            check=True,
        )
        subprocess.run(["kubectl", "delete", "node", name], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Drain failed: {e}")
    return {"success": True, "message": f"Node '{name}' drained and removed"}
