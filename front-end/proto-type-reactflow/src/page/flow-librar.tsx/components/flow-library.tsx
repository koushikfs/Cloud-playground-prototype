import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    Position,
    Handle,
  } from 'reactflow';
import 'reactflow/dist/style.css';

interface DroppableComponentProps {}


interface nodeProps {
  id: any;
  data: any;
  onRemove?: any;
}


export const CustomNode: React.FC<nodeProps> = ({data}) => {
  return (
    <div className="custom-node" style={{  position: 'relative',
    background:'#000', border:'1px solid #fff',
    padding: '8px',
    borderRadius: '4px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    zIndex: 1, }}>
        <Handle type="target" position={Position.Left}  />
          <div className='custom-node-inside' style={{ color:'#000' }}>
            {/* <span>{data.label}</span> */}
            <img src={data.img} />
          </div>
          {/* <button id="close" onClick={onRemove} style={{   position: 'absolute',
    top: '-7px',
    right: '-6px',
    width: '12px',
    height: '12px',
    fontSize: '6px',
    fontWeight: 'bold',
    padding: '0px',
    textAlign: 'center',
    background: 'rgb(255, 255, 255)',
    color: 'rgb(0, 0, 0)',
    border: 'none',
    borderRadius: '9px',
    cursor: 'pointer' }}>
            X
          </button> */}
      <Handle type="source" position={Position.Right} id="b"  />
    </div>
  );
};

const nodeTypes = {
  selectorNode: CustomNode,
};

 
const  ReactFlowCmp: React.FC<DroppableComponentProps> = ({}) => {

  const defaultEdgeOptions = {
    animated: true,
    type: 'smoothstep',
  };

  const connectionLineStyle = { stroke: '#ffff' };

    const reactFlowWrapper = useRef(null);

    const initialNodes: any = []
       
      
      
      
  
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes || []);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
    const [dublicate, setDublicate] = useState(2)
    

    const onConnect = useCallback(
      (params: any) => {
        const { source, target } = params;
    
        // Assuming Edge type is defined somewhere in your code
        type EdgeType = { id: string; source: string; target: string };
    
        // Update the edges state by adding a new edge
        setEdges((prevEdges: EdgeType[]) => [
          ...prevEdges,
          { id: `${source}_to_${target}`, source, target },
        ]);
      },
      []
    );
  

    const onDragOver = useCallback((event: any) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    }, []);
  
    const onDrop = useCallback((event: any) => {
      event.preventDefault();
    
      const type = event.dataTransfer.getData('application/reactflow');
      const img = event.dataTransfer.getData('getImg')
    
      // Check if the dropped element is valid
      if (typeof type === 'undefined' || !type) {
        return;
      }



      const isDuplicate = nodes.some((node) => node?.data?.label === type);
  
      // Calculate the position relative to the ReactFlow container
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      const customData = {
        label: type, // Customize the label as needed
        description: 'Additional information', // Add any other custom properties
        img: img
      };
    
      const newNode = {
        id: isDuplicate ? `${type}-${dublicate}` : type,
        type: 'selectorNode',
        position,
        data: customData,
      };

      if(isDuplicate) {
        setDublicate(dublicate + 1)
      }
    
      setNodes((prevNodes) => [...prevNodes, newNode]);
    }, [ nodes, setNodes, reactFlowInstance, reactFlowWrapper]);

    const onNodeClick = (event: any,id: any) => {
      const clickedElement = event.target;
      if (clickedElement.id === 'close') {
        const updatedNodes = nodes.filter((node) => node.id !== id);
        const updatedEdges = edges.filter((edge) => edge.source !== id && edge.target !== id);
        setNodes(updatedNodes);
        setEdges(updatedEdges);
      }
    };

    const exportToJSON = () => {
      const data = { nodes: nodes, edges: edges };
      const payload = JSON.stringify({ data: JSON.stringify(data) });
      fetch('http://192.168.29.21:80/deploy.php', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: payload,
      })
      .catch(error => {
        console.error('Error:', error);
      });
      window.open('http://192.168.29.21:80/home.html', 'newwindow', 'width=800, height=600');
    }; 

    const destroyAction = () => {
      fetch('http://192.168.29.21:80/destroy.php', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Network response was not ok.');
      })
      .then(jsonResponse => {
        console.log('Success:', jsonResponse);
      })
      .catch(error => {
        console.error('Error:', error);
      });
    };
    

  return (
    <div className='st--library-main' style={{  height: 'calc(100vh - 100px)' }} >

       <ReactFlow
        key={`${nodes.length}-${edges.length}`}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={(event: any, element: any) => {
              if (element?.id && element.type === 'selectorNode') {
                onNodeClick(event,element.id);
              }
            }}
            connectionLineStyle={connectionLineStyle}
            connectionLineType="smoothstep"
            snapToGrid={false}
            attributionPosition="bottom-left"
            defaultEdgeOptions={defaultEdgeOptions}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
          
        <Background variant="dots"  gap={10} size={1} ref={reactFlowWrapper} style={{ border: '1px solid black' }}/>

        
      </ReactFlow>
      <button className='destroy-btn' onClick={destroyAction}>Destroy</button>
      <button className='export-btn' onClick={exportToJSON}>Deploy</button>
      
     
    </div>
  );
}
export default ReactFlowCmp