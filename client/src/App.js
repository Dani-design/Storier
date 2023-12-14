import React, { useState, useEffect } from "react";
import "./index.css";

function App() {
  const [inputString, setInputString] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [existingImagesLoaded, setExistingImagesLoaded] = useState(false);
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
        // If existing images are not loaded yet, set the state to true
        if (!existingImagesLoaded) {
          setExistingImagesLoaded(true);
        }

        // Add the new images to the existing ones
        setResultImages((prevResultImages) => [
          ...prevResultImages,
          ...data.image_responses,
        ]);

        console.log(data);
        setIsLoading(false);
        setInputString("");
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  const handleRefreshStory = () => {
    // Clear the existing images and set the state to false
    setResultImages([]);
    setExistingImagesLoaded(false);
  };

  return (
    <div id="container">
      <div id="images">
        {existingImagesLoaded && resultImages.length === 0 ? (
          <p>No new images. Generate some using the button above.</p>
        ) : (
          //    Used without checking in text for merlin
          //     resultImages.map(({ sentence, image_path }, index) => (
          //       <div key={index}>
          //         <span>{sentence}</span>
          //         <ImageComponent
          //           imagePath={image_path}
          //           altText={`Generated Image ${index + 1}`}
          //         />
          //       </div>
          //     ))
          //   )}
          // </div>
          resultImages.map(({ sentence, image_path }, index) => {
            const cleanedSentence = sentence.replace(
              "(young male wizard with blue hair)",
              ""
            );

            return (
              <div key={index}>
                <span>{cleanedSentence}</span>
                <ImageComponent
                  imagePath={image_path}
                  altText={`Generated Image ${index + 1}`}
                />
              </div>
            );
          })
        )}
      </div>
      <div id="generate">
        <label>
          <p>{isLoading ? "Loading images..." : "Input Prompt"}</p>
          <input
            type="text"
            value={inputString}
            onChange={handleInputChange}
            placeholder="write a prompt"
            disabled={isLoading}
          />
        </label>
        <button onClick={handleStableDiffusion} disabled={isLoading}>
          Generate Images
        </button>
        <button id="refreshStory" onClick={handleRefreshStory}>
          Refresh Story X
        </button>
      </div>
    </div>
  );
}

export default App;
