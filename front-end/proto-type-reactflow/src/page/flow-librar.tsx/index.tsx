import React from 'react';
import ReactFlowCmp from './components/flow-library'
import '../flow-library.scss'
import Widgets from './components/widget';
import  {
    ReactFlowProvider
  } from 'reactflow';

const FlowLibrary: React.FC = () => {

   
    return(
        <div className='st--main-page'>
            <ReactFlowProvider >
                <div className='row-page'>
                    <div  className='column1' ><Widgets  /></div>
                    <div className='column2'><ReactFlowCmp  /></div>
                </div>
            </ReactFlowProvider>
        </div>
    )
};

export default FlowLibrary;