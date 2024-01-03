
import { Route, Routes } from "react-router-dom";
import FlowLibrary from './page/flow-librar.tsx'



function AppRoutes() {
  return (
    <div className="container">
      {/* Defining routes path and rendering components as element */}
      <Routes>
        <Route path="/" element={<FlowLibrary />} />
       {/* <Route path="/course" element={<Courses />} /> */}
          {/*<Route path="/live" element={<Live />} />
        <Route path="/contact" element={<Contact />} /> */}
      </Routes>
    </div>
  );
}

export default AppRoutes;