import { useState } from 'react'
import './App.css'
import React from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

function App() {

  pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

  var dataPdf;
  const [sourcePDF, setSourcePDF] = useState(dataPdf)
  const [user, setUser] = useState("");

  
  const [uploadHidden, setUploadHidden] = useState(true)
  const [downloadHidden, setDownloadHidden] = useState(true)
  const [isPreview, setPreview] = useState(true)
  const [showOrigin, setShowOrigin] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [idDisabled, setIsDisabled] = useState(true)
  const [totalPages, setTotalPages] = useState(1);
  const [pageNumber, setPageNumber] = useState(1);

  const onChangeTex =() => {
    console.log("asdfasdfasdfasdfasdfasdf")
    setIsDisabled(false)
  }
 
  const onDocumentLoadSuccess = ({ numPages }) => {
    setTotalPages(numPages);
    setPageNumber(1)
  }
 
  const previousPage = () => {
    setPageNumber(prevPageNumber => prevPageNumber - 1);
  }
 
  const nextPage = () => {
    setPageNumber(prevPageNumber => prevPageNumber + 1);
  }

  function onClickPreview() {
    console.log("preview")
    const button = document.getElementById("showOrigin")
    if (showOrigin) {
      button.textContent = "show origin"
    }else {
      button.textContent = "show LaTex"
      const img = document.getElementById("imgOrigin")
      img.setAttribute("src", URL.createObjectURL(selectedImage))
    }
    setShowOrigin(!showOrigin)
  }

  function onClickRender() {
    setIsDisabled(true)
    const texText = document.getElementById('TexFrame')
    var text = texText.value
    console.log(text)
    const KeyOptions = {
      method: 'POST',
      headers:{
        'Content-type': 'application/json'
      },
      body: JSON.stringify({
        tex: text
      }),
    };
    fetch(`http://188.44.41.132:8000/renderTex/${user}`, KeyOptions)
    .then(response => {
      if (response.ok) {
        const error = document.getElementById('statusError');
        error.textContent = "";
        return response.blob()
      } else {
        throw new Error('');
      }
    })
    .then(data => {
      setSourcePDF(data)
    }).catch(err => {
      const error = document.getElementById('statusError');
      error.textContent = "Cannot render this tex file or files has been deleted (files stores only for 30 minutes)"
    })
  }

  function onDownloadBtn() {
    const options = {
      method: 'GET',
    };
    fetch(`http://188.44.41.132:8000/zip/${user}/`, options)
    .then(response => response.blob())
    .then(data => {
      const download = document.createElement('a')
      download.href = URL.createObjectURL(data)
      download.download = "files.zip"
      download.click()
    })
  }

  function onUploadBtnClicked() {
    setPreview(false);
    const error = document.getElementById('statusError');
    error.textContent = ""
    console.log("something")
    const fileInput = document.querySelector('input[type="file"]') ;
    const formData = new FormData();
    setSelectedImage(fileInput.files[0])
    formData.append('file', fileInput.files[0]);
    const KeyOptions = {
      method: 'POST',
      body: formData,
    };
    
    console.log("fetching")
    setUploadHidden(false)
    fetch('http://188.44.41.132:8000/uploadFile', KeyOptions)
    .then(responce => responce.text())
    .then(data => {
      const options = {
        method: 'GET',
        
      };
    console.log(data)
    data = data.substring(1,data.length-1)
    setUser(data)
    console.log(user);
      fetch(`http://188.44.41.132:8000/tex/${data}/`, options)
      .then(response => {
        if (response.ok)
          return response.text()
        else
          throw new Error('');
      })
      .then(data => {
        data = data.substring(1, data.length - 1);
        let str = data;
        
        console.log(str);
        str = str.split("\\n").join("\r\n")
        str = str.split("\\\\").join("\\");
        str = str.split("\noindent").join("\\noindent")
        console.log(str);

        const TexPage = document.getElementById("TexFrame");
        TexPage.value = str;
        setUploadHidden(true)
        setIsDisabled(true)
      }).catch(err => {
        setUploadHidden(true)
        const error = document.getElementById('statusError');
        error.textContent = "Try to upload file again (all files stores only 30 minutes)"
      })


      fetch(`http://188.44.41.132:8000/pdf/${data}/`, options)
      .then(response => {
        if (response.ok)
          return response.blob()
        else
          throw new Error('');
      })
      .then(data=> {
        dataPdf = data;
        setSourcePDF(dataPdf)
        console.log(dataPdf)
        setUploadHidden(true)
      }).catch(err => {
        setUploadHidden(true)
        const error = document.getElementById('statusError');
        error.textContent = "Try to upload file again (all files stores only 30 minutes)"
      })
    })
  }

  return (
    <>
      <div className="App">
      <div className="App-header">
        <div className="MainAppBlock">

          <div className="SpecialButtons">
            <div>
              <button id="showOrigin" type="button" disabled={isPreview} onClick={onClickPreview}>show origin</button>
            </div>
            <div>
              <button hidden={true}></button>
            </div>
          </div>

          <div className="TextBlock" id="texBlock">

            <div className="FilesPreview" hidden={!showOrigin}>
              <div className="documentView">
                <img id="imgOrigin" src="" alt="not found" />
              </div>
            </div>

            <div className="FilesPreview" hidden={showOrigin}>
              <div className='texView'>
                <textarea id="TexFrame" onChange={onChangeTex}>
                </textarea >
              </div>
            </div>

            <div className="FilesPreview" id="texVis">
              <div className='documentView'>
                <Document file={sourcePDF} onLoadSuccess={onDocumentLoadSuccess}>
                  <Page pageNumber={pageNumber}>

                  </Page>
                </Document>
              </div>
            </div>

          </div>

          <div className="SpecialButtons">
            <div>
              <button type="button" disabled={idDisabled} onClick={onClickRender}>render</button>
              <div id='statusError'></div>
            </div>
           <div>
            <button
              type="button"
              disabled={pageNumber <= 1}
              onClick={previousPage}>
              Previous
            </button>
            <button
              type="button"
              disabled={pageNumber >= totalPages}
              onClick={nextPage}>
              Next
            </button>
            </div>
          </div>

          <div className="BtnBlock">
            <div>
                <input type="file" className="DownloadBtn" id="uploadFile"></input>
            </div>
            <div className="SpecialButtons">
              <button className="LoadBtn" id="myButton" onClick={onUploadBtnClicked}> Upload File</button>
              <div>
                <div hidden={uploadHidden}>
                  <span className="loader"></span>
                </div>
              </div>
            </div>
            <div className="SpecialButtons">
              <a id="download">
                <button className="LoadBtn" onClick={onDownloadBtn}> Download LaTex</button>
              </a>
              <div>
                <div hidden={downloadHidden}>
                  <span className="loader"></span>
                </div>
              </div>
            </div>
              
          </div>  

        </div>
        
      </div>
    </div>
    </>
  )
}

export default App
