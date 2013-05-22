;;; Pallet project configuration file

(require '[pallet.crate.git      :as git])
(require '[pallet.crate.postgres :as postgres])
(require '[pallet.actions        :as actions])
(require '[pallet.action         :as action])

(def github-gittip
  "git://github.com/gittip/www.gittip.com.git")

(def postgres-local-trust
  {:permissions [{:connection-type :local
                  :database :all
                  :user :postgres
                  :auth-method :peer}
                 {:connection-type :local
                  :database :all
                  :user :all
                  :auth-method :trust}
                 {:connection-type :host
                  :database :all
                  :user :all
                  :ip-mask "127.0.0.1/32"
                  :auth-method :trust}
                 {:connection-type :host
                  :database :all
                  :user :all
                  :ip-mask "::1/128"
                  :auth-method :trust}]})

(defplan compile-deps
  "Compile dependencies"
  []
  (actions/packages :aptitude
                    ["gcc" "make" "python-dev"
                     "postgresql-client"
                     "postgresql-contrib"
                     "postgresql-server-dev-9.1"
                     "ruby-sass"])
  (action/with-action-options
    {:script-prefix :no-sudo
     :script-dir "www.gittip.com"}
    (actions/exec-script ("make" "env"))))

(def base-node-spec
  {:image {:os-family :ubuntu
           :os-version-matches "12.04"}})

(defproject www.gittip.com
  :provider {:aws-ec2
             {:node-spec base-node-spec
              :selectors #{:default}}}

  :groups [(group-spec
            "gittip-single"
            :node-spec (conj base-node-spec
                             {:network {:inbound-ports [22 8537]}})
            :extends [(git/server-spec {})
                      (postgres/server-spec postgres-local-trust)]
            :phases {:install (plan-fn
                               (action/with-action-options
                                 {:script-prefix :no-sudo}
                                 (git/clone github-gittip))
                               (compile-deps))
                     :configure (plan-fn
                                 (postgres/create-role
                                  (System/getenv "USER")
                                  :user-parameters [:login :superuser])
                                 (actions/exec-script
                                  ("service" "postgresql" "restart")
                                  ("chown" "-R"
                                   ~(System/getenv "USER")
                                   "www.gittip.com")))
                     :test (plan-fn
                            (action/with-action-options
                              {:script-dir "www.gittip.com"}
                              (actions/exec-script ("make" "test"))))})])
