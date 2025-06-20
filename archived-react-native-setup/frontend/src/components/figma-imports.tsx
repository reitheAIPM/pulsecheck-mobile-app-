import React, { useState, useEffect } from "react";
import { BuilderComponent, builder, useIsPreviewing } from "@builder.io/react";
import { View, Text, StyleSheet } from "react-native";

// Builder Public API Key
builder.init("93b18bce96bf4218884de91289488848");

export default function BuilderPage() {
  const isPreviewingInBuilder = useIsPreviewing();
  const [notFound, setNotFound] = useState(false);
  const [content, setContent] = useState<any>(null);

  // get the page content from Builder
  useEffect(() => {
    async function fetchContent() {
      try {
        const content = await builder
          .get("figma-imports", {
            url: window.location.pathname,
          })
          .promise();

        setContent(content);
        setNotFound(!content);

        // if the page title is found,
        // set the document title
        if (content?.data.title) {
          document.title = content.data.title;
        }
      } catch (error) {
        console.error("Error fetching Builder content:", error);
        setNotFound(true);
      }
    }
    fetchContent();
  }, []);

  if (content === null) {
    return (
      <View style={styles.loading}>
        <Text>Loading...</Text>
      </View>
    );
  }

  // If no page is found, return
  // a 404 page from your code.
  if (notFound && !isPreviewingInBuilder) {
    return (
      <View style={styles.notFound}>
        <Text>404 Page Not Found</Text>
      </View>
    );
  }

  // return the page when found
  return (
    <View style={styles.container}>
      {/* Render the Builder page */}
      <BuilderComponent model="figma-imports" content={content} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notFound: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
}); 