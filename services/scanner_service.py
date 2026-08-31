import cv2
import numpy as np


class ScannerService:

    @staticmethod
    def scan_document(image_path):

        image = cv2.imread(image_path)

        if image is None:
            return image_path

        ratio = image.shape[0] / 500.0

        original = image.copy()

        image = cv2.resize(image, (int(image.shape[1]/ratio),500))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(gray,(5,5),0)

        edged = cv2.Canny(gray,75,200)

        contours,_ = cv2.findContours(
            edged,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )[:5]

        screenCnt = None

        for c in contours:

            peri = cv2.arcLength(c,True)

            approx = cv2.approxPolyDP(
                c,
                0.02*peri,
                True
            )

            if len(approx)==4:

                screenCnt = approx

                break

        if screenCnt is None:

            return image_path

        pts = screenCnt.reshape(4,2)*ratio

        rect = ScannerService.order_points(pts)

        (tl,tr,br,bl)=rect

        widthA=np.linalg.norm(br-bl)

        widthB=np.linalg.norm(tr-tl)

        maxWidth=max(int(widthA),int(widthB))

        heightA=np.linalg.norm(tr-br)

        heightB=np.linalg.norm(tl-bl)

        maxHeight=max(int(heightA),int(heightB))

        dst=np.array([
            [0,0],
            [maxWidth-1,0],
            [maxWidth-1,maxHeight-1],
            [0,maxHeight-1]
        ],dtype="float32")

        M=cv2.getPerspectiveTransform(rect,dst)

        warped=cv2.warpPerspective(
            original,
            M,
            (maxWidth,maxHeight)
        )

        cv2.imwrite(image_path,warped)

        return image_path


    @staticmethod
    def order_points(pts):

        rect=np.zeros((4,2),dtype="float32")

        s=pts.sum(axis=1)

        rect[0]=pts[np.argmin(s)]

        rect[2]=pts[np.argmax(s)]

        diff=np.diff(pts,axis=1)

        rect[1]=pts[np.argmin(diff)]

        rect[3]=pts[np.argmax(diff)]

        return rect