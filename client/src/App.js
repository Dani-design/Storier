import React, { useState, useEffect } from "react";
import "./index.css";

function App() {
  const [inputString, setInputString] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resultImages, setResultImages] = useState([]);

  const ImageComponent = ({ imagePath, altText }) => {
    const [imageSrc, setImageSrc] = useState(null);

    useEffect(() => {
      import(`./generated_images/${imagePath}`)
        .then((module) => setImageSrc(module.default))
        .catch((error) => console.error("Error importing image:", error));
    }, [imagePath]);

    return imageSrc ? (
      <img src={imageSrc} alt={altText} style={{ maxWidth: "100%" }} />
    ) : null;
  };

  const handleInputChange = (event) => {
    setInputString(event.target.value);
  };

  const handleStableDiffusion = () => {
    setIsLoading(true);
    fetch("http://localhost:5000/stablediffusion", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: inputString }),
    })
      .then((res) => res.json())
      .then((data) => {
        setResultImages(data.image_responses);
        console.log(data);
        setIsLoading(false);
        setInputString("");
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  return (
    <div id="container">
      <div id="images">
        {isLoading ? (
          <p>Loading...</p>
        ) : resultImages.length > 0 ? (
          resultImages.map(({ sentence, image_path }, index) => (
            <div key={index}>
              <span>{sentence}</span>
              <ImageComponent
                imagePath={image_path}
                altText={`Generated Image ${index + 1}`}
              />
            </div>
          ))
        ) : null}
      </div>
      <div id="generate">
        <label>
          <p>Input Prompt</p>
          <input
            type="text"
            value={inputString}
            onChange={handleInputChange}
            placeholder="write a prompt"
          />
        </label>
        <button onClick={handleStableDiffusion}>Generate Images</button>
      </div>
    </div>
  );
}

export default App;
