(defproject www.gittip.com "0.0.0"
  :plugins [[com.palletops/pallet-lein "0.6.0-beta.6"]]
  :profiles {:pallet
             {:dependencies
              [[com.palletops/pallet "0.8.0-beta.10"
                ;; avoid using an old version
                :exclusions [org.clojure/tools.logging]]
               ;;[com.palletops/java-crate "0.8.0-beta.5"]
               [com.palletops/git-crate "0.8.0-alpha.2"]
               [com.palletops/postgres-crate "0.8.0-313-SNAPSHOT"
                :exclusions [com.palletops/pallet]]
               [org.cloudhoist/pallet-jclouds "1.5.2"]
               [org.jclouds/jclouds-allblobstore "1.5.5"]
               [org.jclouds/jclouds-allcompute "1.5.5"]
               [org.jclouds.driver/jclouds-slf4j "1.5.5"
                ;; avoid using an old version
                :exclusions [org.slf4j/slf4j-api]]
               [org.jclouds.driver/jclouds-sshj "1.5.5"]]}})
