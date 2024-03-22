import * as React from "react";
const SvgHome = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlSpace="preserve"
    viewBox="0 0 100 125"
    {...props}
  >
    <path d="M75.61 84.38c1.4 0 2.54-1.13 2.54-2.54V54.68h6.68a4.41 4.41 0 0 0 4.41-4.41c0-1.39-.65-2.63-1.65-3.44l-8.63-7.48V26.89c0-1.46-1.18-2.64-2.63-2.64h-5.46c-1.46 0-2.64 1.18-2.64 2.64v3.14L52.89 16.7a4.41 4.41 0 0 0-5.78 0L12.28 46.94a4.43 4.43 0 0 0-1.24 4.88 4.42 4.42 0 0 0 4.13 2.87h6.68v27.16c0 1.41 1.14 2.54 2.54 2.54H39.4V64.63c0-2.79 2.26-5.05 5.05-5.05h11.11c2.79 0 5.05 2.26 5.05 5.05v19.74h15z" />
    <text
      y={115}
      fontFamily="'Helvetica Neue', Helvetica, Arial-Unicode, Arial, Sans-serif"
      fontSize={5}
      fontWeight="bold"
    >
      {"Created by Marcio Silveira"}
    </text>
    <text
      y={120}
      fontFamily="'Helvetica Neue', Helvetica, Arial-Unicode, Arial, Sans-serif"
      fontSize={5}
      fontWeight="bold"
    >
      {"from the Noun Project"}
    </text>
  </svg>
);
export default SvgHome;
