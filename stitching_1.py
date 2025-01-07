import cv2
import numpy as np

# Load images
img1 = cv2.imread('C:/Users/Bende/Documents/blender_hangar/render_1.png')
img2 = cv2.imread('C:/Users/Bende/Documents/blender_hangar/render_5.png')

# Detect features and compute descriptors
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# Match features using BFMatcher
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# Apply ratio test to filter good matches
good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

# Check if there are enough matches
if len(good_matches) > 10:
    # Extract matched points
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Compute homography matrix
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # Determine the size of the resulting panorama
    height1, width1 = img1.shape[:2]
    height2, width2 = img2.shape[:2]

    # Get the corners of both images in the final frame
    corners1 = np.float32([[0, 0], [0, height1], [width1, height1], [width1, 0]]).reshape(-1, 1, 2)
    corners2 = np.float32([[0, 0], [0, height2], [width2, height2], [width2, 0]]).reshape(-1, 1, 2)

    # Transform corners of img1 using homography
    transformed_corners1 = cv2.perspectiveTransform(corners1, H)

    # Combine corners from both images to determine the size of the panorama
    all_corners = np.concatenate((transformed_corners1, corners2), axis=0)
    [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel())
    [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel())

    # Translation matrix to handle negative coordinates
    translation_dist = [-x_min, -y_min]
    H_translation = np.array([[1, 0, translation_dist[0]],
                              [0, 1, translation_dist[1]],
                              [0, 0, 1]])

    # Warp img1 to panorama space
    result = cv2.warpPerspective(img1, H_translation @ H, (x_max - x_min, y_max - y_min))

    # Paste img2 into the panorama
    result[translation_dist[1]:translation_dist[1] + height2, 
           translation_dist[0]:translation_dist[0] + width2] = img2

    # Save and display result
    cv2.imwrite('stitched_image.png', result)
    # cv2.imshow('Stitched Image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Not enough good matches found!")
