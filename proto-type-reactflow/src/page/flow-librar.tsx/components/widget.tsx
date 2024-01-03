import React from 'react';
import '../../flow-library.scss';
import Elb from '../../.././img/elb.jpeg';
import Ec2 from '../../.././img/ec2.jpeg';
import s3 from '../../.././img/s3.jpeg';

interface MyComponentProps {
    
  }


const Widgets: React.FC<MyComponentProps> = () => {
    const onDragStart = (event: any, nodeType: any, img: any) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.setData('getImg', img);
        event.dataTransfer.effectAllowed = 'move';
      };
    
    const arr =  [{img: s3, name:'s3'},{img: Ec2, name:'ec2'},{img: Elb, name:'elb'}]
    return(
        <div className='st--widgets-main'>
        { arr.map((number) => (
            <div onDragStart={(event) => onDragStart(event, number.name, number.img)} draggable   className='st--widget-conatiner' > 
            <img src={number.img} />
            <span>{number.name}</span>
            </div>
        ))}
          
        </div>
    )
}


export default Widgets